import json as jsn
import os
import pillow_heif
import shutil
from PIL import Image
from pathlib import Path

from typing import Callable, Any, Optional

SORTING_METHODS: dict[str, Callable[..., Any]] = {}

def register(name: Optional[str] = None):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        SORTING_METHODS[name or func.__name__] = func
        return func
    return decorator


def move(filter_group_names:list[str], image_path: Path, output_folder:Path):
    """makes (a) subfolder(s) in the output_folder named according to the filter_group_names(or just check if they exist and are writable if it already exists), moves copies of the original image in those folders and then deletes the original image folder"""
    for f in filter_group_names:
        fg_folder = output_folder / f
        fg_folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(image_path,fg_folder)
    os.remove(image_path)

def link(filter_group_names:list[str], image_path: Path, output_folder:Path):
    """makes (a) subfolder(s) in the output_folder named according to the filter_group_names(or just check if they exist and are writable if it already exists) and places a symlink of the original image in those folders."""
    for f in filter_group_names:
        fg_folder = output_folder / f
        fg_folder.mkdir(parents=True, exist_ok=True)
        os.symlink(image_path.resolve(), fg_folder / image_path.name)

def tag(filter_group_names:list[str], image_path: Path, output_folder:Optional[Path] = None):
    """appends filter_group_names seperated with commas to the exif metadata description"""
    img = Image.open(image_path)
    exif_data = img.getexif()
    tags_str = ", ".join(filter_group_names)
    exif_data[270] = tags_str  # 270 is ImageDescription tag
    img.save(image_path, exif=exif_data)

def name(filter_group_names:list[str], image_path: Path, output_folder:Optional[Path] = None):
    """changes the image file name to: `{filter_group_names(seperated with underscores)}{index of picture with the same filter_group_names combination}`"""
    new_name = "_".join(filter_group_names) + image_path.suffix
    new_path = image_path.parent / new_name
    image_path.rename(new_path)

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

def none(filter_group_names:Optional[list[str]] = None, image_path:Optional[Path] = None, output_folder:Optional[Path] = None):
    pass

def sort(method_name:str, filter_group_names:list[str], image_path: Path, output_folder:Path):
    SORTING_METHODS[method_name](filter_group_names=filter_group_names, image_path=image_path, output_folder=output_folder)