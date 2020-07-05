import os
from PIL import Image
import PIL
import glob
from pathlib import Path
from tqdm import tqdm
import zipfile

## Parameters

BOX = (1,10,23,34)   # cropping box parameters
BACKGROUND = (255,255,255) # white border
OLD_FOLDER = 'kanjis'
NEW_FOLDER = 'kanjis_edited'

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))
            
def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

def expand2square(pil_img, background_color):
    width, height = pil_img.size
    if width == height:
        return pil_img
    elif width > height:
        result = Image.new(pil_img.mode, (width, width), background_color)
        result.paste(pil_img, (0, (width - height) // 2))
        return result
    else:
        result = Image.new(pil_img.mode, (height, height), background_color)
        result.paste(pil_img, ((height - width) // 2, 0))
        return result

if __name__ == '__main__':
    print(f"Converting files, cropping, removing alpha channel and pasting to {NEW_FOLDER}")
    
    Path(NEW_FOLDER).mkdir(parents=True, exist_ok=True)

    file_list = glob.glob(os.path.join(OLD_FOLDER, '*.jpg'))
    print(len(file_list))

    i = 0
    for old_path in tqdm(file_list):
        file_name = Path(old_path).parts[-1]
        try:
            new_image = Image.\
                open(old_path).\
                crop(box=BOX).\
                convert('RGB')

            new_image = add_margin(
                expand2square(new_image, BACKGROUND),
                2,2,2,2,BACKGROUND)
            
            assert new_image.size == (28,28), "Image has wrong dimensions"
            new_image.save(os.path.join(NEW_FOLDER, file_name))
            
        except PIL.UnidentifiedImageError:
            print(f"Could not read {file_name}")
            i += 1

    print(f"Out of {len(file_list)} files, could not read {i}")
    
    print("Zipping and saving to processed_images.zip")
    with zipfile.ZipFile('processed_images.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(os.path.join('.', NEW_FOLDER), zipf)
