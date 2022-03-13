import proxyshop.constants as con
import photoshop.api as ps
app = ps.Application()

def fix_color_pair(input):
    # Utility def to standardise ordering of color pairs, e.g. "UW" becomes "WU"
    color_pairs = [
        con.layers['WU'], 
        con.layers['UB'], 
        con.layers['BR'], 
        con.layers['RG'], 
        con.layers['GW'], 
        con.layers['WB'], 
        con.layers['BG'], 
        con.layers['GU'], 
        con.layers['UR'], 
        con.layers['RW']
    ]
    for colorPair in color_pairs:
        if input.find(colorPair[0]) >= 0:
            if input.find(colorPair[1]) >= 0:
                return colorPair

def select_frame_layers(mana_cost, type_line, oracle_text, color_identity_array):
    colors = [
        con.layers['WHITE'], 
        con.layers['BLUE'], 
        con.layers['BLACK'], 
        con.layers['RED'], 
        con.layers['GREEN']
    ]
    basic_colors = { 
        "Plains": con.layers['WHITE'], 
        "Island": con.layers['BLUE'], 
        "Swamp": con.layers['BLACK'], 
        "Mountain": con.layers['RED'], 
        "Forest": con.layers['GREEN'] 
    }
    hybrid_symbols = ["W/U", "U/B", "B/R", "R/G", "G/W", "W/B", "B/G", "G/U", "U/R", "R/W"]

    if type_line.find(con.layers['LAND']) >= 0:
        # Land card
        twins = ""
        # Check if it has a basic land subtype
        basic_identity = ""

        for basic in basic_colors:
            if type_line.find(basic) >= 0:
                # The land has this basic type on its type_line
                basic_identity += basic_colors[basic]

        if len(basic_identity) == 1:
            # The land has exactly one basic land type. We still need to get the pinlines from the total colors the card
            # can add though (cornercase: Murmuring Bosk)
            twins = basic_identity
        elif len(basic_identity) == 2:
            # The land has exactly two basic land types. Ensure they follow the correct naming convention, then
            # return the corresponding frame elements
            basic_identity = fix_color_pair(basic_identity)
            return {
                'background': con.layers['LAND'],
                'pinlines': basic_identity,
                'twins': con.layers['LAND'],
                'is_colorless': False
            }

        # Array of rules text lines in the card
        rules_lines = oracle_text.split("\n")
        colors_tapped = ""

        # Iterate over rules text lines
        for line in rules_lines:

            # Identify if the card is a fetchland of some kind
            if line.lower().find("search your library") >= 0:
                if line.lower().find("cycling") < 0:
                    # Card is a fetchland of some kind
                    # Find how many basic land types the ability mentions
                    basic_identity = ""
                    for basic in basic_colors:
                        if line.find(basic) >= 0:
                            # The land has this basic type in the line of rules text where it fetches
                            basic_identity = basic_identity + basic_colors[basic]

                # Set the name box & pinlines based on how many basics the ability mentions
                if len(basic_identity) == 1:
                    # One basic mentioned - the land should just be this color
                    return {
                        'background': con.layers['LAND'],
                        'pinlines': basic_identity,
                        'twins': basic_identity,
                        'is_colorless': False,
                    }
                elif len(basic_identity) == 2:
                    # Two basics mentioned - the land should use the land name box and those pinlines
                    basic_identity = fix_color_pair(basic_identity)
                    return {
                        'background': con.layers['LAND'],
                        'pinlines': basic_identity,
                        'twins': con.layers['LAND'],
                        'is_colorless': False,
                    }
                elif len(basic_identity) == 3:
                    # Three basic mentioned - panorama land
                    return {
                        'background': con.layers['LAND'],
                        'pinlines': con.layers['LAND'],
                        'twins': con.layers['LAND'],
                        'is_colorless': False,
                    }
                elif line.find(con.layers['LAND'].lower()) >= 0:
                    # Assume we get here when the land fetches for any basic
                    if line.find("tapped") < 0 or line.find("untap") >= 0:
                        # Gold fetchland
                        return {
                            'background': con.layers['LAND'],
                            'pinlines': con.layers['GOLD'],
                            'twins': con.layers['GOLD'],
                            'is_colorless': False,
                        }
                    else:
                        # colorless fetchland
                        return {
                            'background': con.layers['LAND'],
                            'pinlines': con.layers['LAND'],
                            'twins': con.layers['LAND'],
                            'is_colorless': False,
                        }

            # Check if the line adds one mana of any color
            if line.lower().find("add") >= 0 and line.find("mana") >= 0:
                if ( line.find("color ") > 0 
                    or line.find("colors ") > 0
                    or line.find("color.") > 0 
                    or line.find("colors.") > 0
                ):
                    # Identified an ability of a potentially gold land
                    # If the ability doesn't include the phrases "enters the battlefield", "Remove a charge
                    # counter", and "luck counter", and doesn't include the word "Sacrifice", then it's
                    # considered a gold land
                    if ( line.find("enters the battlefield") < 0 
                        and line.find("Remove a charge counter") < 0
                        and line.find("Sacrifice") < 0 
                        and line.find("luck counter") < 0
                    ):
                        # This is a gold land - use gold twins and pinlines
                        return {
                            'background': con.layers['LAND'],
                            'pinlines': con.layers['GOLD'],
                            'twins': con.layers['GOLD'],
                            'is_colorless': False,
                        }

            # Count how many colors of mana the card can explicitly tap to add
            tap_index = line.find("{T}")
            colon_index = line.find(":")
            if tap_index < colon_index and line.lower().find("add") >= 0:
                # This line taps to add mana of some color
                # Count how many colors the line can tap for, and add them all to colors_tapped
                for color in colors:
                    if line.find("{"+color+"}") >= 0 and colors_tapped.find(color) < 0:
                        # Add this color to colors_tapped
                        colors_tapped = colors_tapped + color

        # Evaluate colors_tapped and make decisions from here
        if len(colors_tapped) == 1:
            pinlines = colors_tapped
            if twins == "": twins = colors_tapped
        elif len(colors_tapped) == 2:
            colors_tapped = fix_color_pair(colors_tapped)
            pinlines = colors_tapped
            if twins == "": twins = con.layers['LAND']
        elif len(colors_tapped) > 2:
            pinlines = con.layers['GOLD']
            if twins == "": twins = con.layers['GOLD']
        else:
            pinlines = con.layers['LAND']
            if twins == "": twins = con.layers['LAND']

        # Final return statement
        return {
            'background': con.layers['LAND'],
            'pinlines': pinlines,
            'twins': twins,
            'is_colorless': False,
        }
    else:
        # Nonland card

        # Decide on the color identity of the card, as far as the frame is concerned
        # e.g. Noble Hierarch's color identity is [W, U, G], but the card is considered green, frame-wise
        color_identity = ""
        if mana_cost == "" or (mana_cost == "{0}" and type_line.find(con.layers['ARTIFACT']) < 0):
            # Card with no mana cost
            # Assume that all nonland cards with no mana cost are mono-colored
            if color_identity_array == None: color_identity = ""
            # else color_identity = color_identity_array[0]
            else:
                color_identity = "".join(color_identity_array)
                if len(color_identity) == 2: color_identity = fix_color_pair(color_identity)
        else:
            # The card has a non-empty mana cost
            # Loop over each color of mana, and add it to the color identity if it's in the mana cost
            for color in colors:
                if mana_cost.find("{"+color) >= 0 or mana_cost.find(color+"}") >= 0:
                    color_identity = color_identity + color

        # If the color identity is exactly two colors, ensure it fits into the proper naming convention
        # e.g. "WU" instead of "UW"
        if len(color_identity) == 2: color_identity = fix_color_pair(color_identity)

        # Handle Transguild Courier case - cards that explicitly state that they're all colors
        if oracle_text.find(" is all colors.") > 0: color_identity = "WUBRG"

        # Identify if the card is a full-art colorless card, e.g. colorless
        # Assume all non-land cards with the word "Devoid" in their rules text use the BFZ colorless frame
        devoid = bool(oracle_text.find("Devoid") >= 0 and len(color_identity) > 0)
        if (len(color_identity) <= 0 and type_line.find(con.layers['ARTIFACT']) < 0) or devoid or (mana_cost == "" and type_line.find("Eldrazi") >= 0):
            # colorless-style card identified
            background = con.layers['COLORLESS']
            pinlines = con.layers['COLORLESS']
            twins = con.layers['COLORLESS']

            # Handle devoid frame
            if devoid:
                # Select the name box and devoid-style background based on the color identity
                if len(color_identity) > 1:
                    # Use gold namebox and devoid-style background
                    twins = con.layers['GOLD']
                    background = con.layers['GOLD']
                else:
                    # Use mono colored namebox and devoid-style background
                    twins = color_identity 
                    background = color_identity

            # Return the selected elements
            return {
                'background': background,
                'pinlines': pinlines,
                'twins': twins,
                'is_colorless': True,
            }

        # Identify if the card is a two-color hybrid card
        hybrid = False
        if len(color_identity) == 2:
            for hybrid_symbol in hybrid_symbols:
                if mana_cost.find(hybrid_symbol) >= 0:
                    # The card is two colors and has a hybrid symbol in its mana cost
                    hybrid = True 
                    break

        # Select background
        if type_line.find(con.layers['ARTIFACT']) >= 0:
            background = con.layers['ARTIFACT']
        elif hybrid: background = color_identity
        elif len(color_identity) >= 2: background = con.layers['GOLD']
        else: background = color_identity

        # Identify if the card is a vehicle, and override the selected background if necessary
        if type_line.find(con.layers['VEHICLE']) >= 0: background = con.layers['VEHICLE']

        # Select pinlines
        if len(color_identity) <= 0: pinlines = con.layers['ARTIFACT']
        elif len(color_identity) <= 2: pinlines = color_identity
        else: pinlines = con.layers['GOLD']

        # Select name box
        if len(color_identity) <= 0: twins = con.layers['ARTIFACT']
        elif len(color_identity) == 1: twins = color_identity
        elif hybrid: twins = con.layers['LAND']
        elif len(color_identity) >= 2: twins = con.layers['GOLD']

        # Finally, return the selected layers
        return {
            'background': background,
            'pinlines': pinlines,
            'twins': twins,
            'is_colorless': False,
        }