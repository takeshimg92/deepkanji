import os
from PIL import Image
import PIL
import glob
from pathlib import Path
from tqdm import tqdm
import zipfile

## Parameters

BOX = (1,10,23,34)   # cropping box parameters
OLD_FOLDER = 'kanjis'
NEW_FOLDER = 'kanjis_edited'

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

if __name__ == '__main__':
    print(f"Converting files, cropping, removing alpha channel and pasting to {NEW_FOLDER}")
    
    Path(NEW_FOLDER).mkdir(parents=True, exist_ok=True)

    file_list = glob.glob(os.path.join(OLD_FOLDER, '*.jpg'))
    print(len(file_list))

    i = 0
    for old_path in tqdm(file_list):
        file_name = Path(old_path).parts[-1]
        try:
            Image.\
                open(old_path).\
                crop(box=BOX).\
                convert('RGB').\
                save(os.path.join(NEW_FOLDER, file_name))
        except PIL.UnidentifiedImageError:
            print(f"Could not read {file_name}")
            i += 1

    print(f"Out of {len(file_list)} files, could not read {i}")
    
    print("Zipping and saving to processed_images.zip")
    with zipfile.ZipFile('processed_images.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(os.path.join('.', NEW_FOLDER), zipf)
