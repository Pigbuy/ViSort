import json
from pathlib import Path
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()

files = [f for f in Path("/home/felix/Documents/Programming/ViSort/test/Input").iterdir() if f.is_file()]

for f in files:
    img = Image.open(f)
    exif = img.getexif()

#jayson = {"desc_author_llm": "test_model", "desc": "an image definetely"}
    exif[0x010E] = ""#json.dumps(jayson).encode()
    img.save(f,exif=exif)