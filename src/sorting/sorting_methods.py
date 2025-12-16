import json as jsn
import os
import pillow_heif
import shutil
from PIL import Image
from pathlib import Path

from logger import logger

from typing import Callable, Any, Optional

SORTING_METHODS: dict[str, Callable[..., Any]] = {}

def register_sm(name: Optional[str] = None):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        SORTING_METHODS[name or func.__name__] = func
        return func
    return decorator

@register_sm("move")
def move(filter_group_names:list[str], image_path: Path, output_folder:Path):
    """makes (a) subfolder(s) in the output_folder named according to the filter_group_names(or just check if they exist and are writable if it already exists), moves copies of the original image in those folders and then deletes the original image folder"""
    amount_skipped = 0
    for f in filter_group_names:
        fg_folder = output_folder / f
        fg_folder.mkdir(parents=True, exist_ok=True)
        if not (fg_folder / image_path.name).exists():
            shutil.copy2(image_path,fg_folder)
        else:
            logger.warning(f"{(fg_folder / image_path.name)} already exists, skipping")
            amount_skipped += 1
    if not (amount_skipped == len(filter_group_names)):
        os.remove(image_path)
    else:
        logger.warning(f"did not remove {image_path} because a file with the same name was everywhere it couldve been sorted to")

@register_sm("link")
def link(filter_group_names:list[str], image_path: Path, output_folder:Path):
    """makes (a) subfolder(s) in the output_folder named according to the filter_group_names(or just check if they exist and are writable if it already exists) and places a symlink of the original image in those folders."""
    for f in filter_group_names:
        fg_folder = output_folder / f
        fg_folder.mkdir(parents=True, exist_ok=True)
        if not (fg_folder / image_path.name).exists():
            os.symlink(image_path.resolve(), fg_folder / image_path.name)

@register_sm("tag")
def tag(filter_group_names:list[str], image_path: Path, output_folder:Optional[Path] = None):
    """appends filter_group_names seperated with commas to the exif metadata description"""
    img = Image.open(image_path)
    exif_data = img.getexif()
    tags_str = ", ".join(filter_group_names) #TODO fix this shit of a tag function to make it append to the json or make a new json in the desc tag
    exif_data[0x010E] = tags_str  # 270 is ImageDescription tag
    img.save(image_path, exif=exif_data)

@register_sm("name")
def name(filter_group_names:list[str], image_path: Path, output_folder:Optional[Path] = None):
    """changes the image file name to: `{filter_group_names(seperated with underscores)}{index of picture with the same filter_group_names combination}`"""
    new_name = "_".join(filter_group_names) + image_path.suffix
    new_path = image_path.parent / new_name
    if not image_path.exists():
        image_path.rename(new_path)
    else:
        logger.warning(f"could not rename '{image_path}' because the file already exists")

@register_sm("json")
def json(filter_group_names:list[str], image_path: Path, output_folder:Path):
    """Create/update ViSort.json(located in the output_folder) with the image added to the given filter groups."""
    json_path = output_folder / "ViSort.json"
    image_str = str(image_path)

    if json_path.exists():
        with open(json_path) as f:
            data = jsn.load(f)
    else:
        data = {}

    for fgn in filter_group_names:
        data.setdefault(fgn, [])
        data[fgn].append(image_str)
    
    with open(json_path, "w") as f:
        jsn.dump(data, f, indent=2)

@register_sm("none")
def none(filter_group_names:Optional[list[str]] = None, image_path:Optional[Path] = None, output_folder:Optional[Path] = None):
    pass

def sort(method_name:str, filter_group_names:list[str], image_path: Path, output_folder:Path):
    SORTING_METHODS[method_name](filter_group_names=filter_group_names, image_path=image_path, output_folder=output_folder)