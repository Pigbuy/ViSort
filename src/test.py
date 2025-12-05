from pathlib import Path
from PIL import Image
import pillow_heif
from typing import Optional
from datetime import datetime

pillow_heif.register_heif_opener()

images = ("test/Input/Adress.jpg", "test/Input/None.jpg", "test/Input/CoordsHEIC.heic", "test/Input/Coords.jpg")


for image in images:
    img = Image.open(image)
    exif = img.getexif()
    raw = exif.get(306)
    if raw is None:
        print("no date found")
    else:
        dt = datetime.strptime(raw, "%Y:%m:%d %H:%M:%S") # type: ignore[arg-type]
        print(f"{image}: {dt}")

