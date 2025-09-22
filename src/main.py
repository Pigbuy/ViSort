import argparse
import configparser
from lists import ValidArgs
import os
from pathlib import Path
from PIL import Image

import asyncio
from concurrent.futures import ThreadPoolExecutor

args = vars(argparse.ArgumentParser().parse_args()) #read cmd args as dict

#replace short arg name with long one
for arg in tuple(args.keys()):
    for sh_arg in ValidArgs:
        if arg == sh_arg.short:
            args[sh_arg.name] = args.pop(arg)

# Read the configuration file
config = configparser.ConfigParser() #this is where the config is gonna be accessible from

config_file = args.get(ValidArgs.config_location.name, ValidArgs.config_location.default) # if config file position is given use that, if not, use default
successfull_reads = config.read(
    config_file
)
if not successfull_reads:
    raise FileNotFoundError(f"Failed to read config file(s): {config_file}")

# get important folder paths and associate them with their name
folders = {
    folder_type: args.get(folder_type.name, folder_type.default)
    for folder_type in ValidArgs
    if folder_type.arg_type == "folder"
}

# make folders if they don't exist yet
for folder in folders.values():
    os.makedirs(folder, exist_ok=True)


# get flags
flags = [
    flag_type
    for flag_type in ValidArgs
    if (flag_type.arg_type == "binary")
    and (flag_type.name in args.keys())
]


def is_image(img:Path):
    try:
        image = Image.open(img)
        image.verify()
        # dont pass non-jpegs as images if no_autoconvert flag is set
        if image.format != "JPEG" and ValidArgs.no_auto_convert in flags:
            return False
        return True
    except Exception:
        return False

# make image set with only valid images ready for conversion
input_folder = Path(folders[ValidArgs.input_location])
images = [
    f 
    for f in input_folder.iterdir() 
    if f.is_file() 
    and is_image(f)
]

# make image queue with only jpeg images
image_queue:list[Path] = []
for imgp in images:
    if not ValidArgs.no_auto_convert in flags:
        image = Image.open(imgp)
        #convert image to jpeg if different format
        if image.format != "JPEG":
            image = image.convert("RGB")
            new_path = imgp.with_suffix(".jpg")
            image.save(new_path, "JPEG")
            imgp.unlink(missing_ok=True)
            imgp = new_path
    image_queue.append(imgp)


