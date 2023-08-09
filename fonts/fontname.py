import os
from fontTools.ttLib import TTFont

def check_font_names(directory):
    font_files = [f for f in os.listdir(directory) if f.endswith('.ttf') or f.endswith('.otf')]

    for font_file in font_files:
        font = TTFont(os.path.join(directory, font_file))

        # 'name' table
        name_records = font.get('name').names

        for name_record in name_records:
            if name_record.nameID == 4:    # 4代表name
                print(f"Font {font_file} 'name' : {name_record.toUnicode()}")
            elif name_record.nameID == 6:  # 6代表postscript name
                print(f"Font {font_file} 'postscript name' : {name_record.toUnicode()}")

        font.close()

# 调用这个函数并传入你想要检查的文件夹路径
check_font_names('.')