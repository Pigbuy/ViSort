import argparse
import configparser
from lists import ValidArgs
import os

args = vars(argparse.ArgumentParser().parse_args()) #read cmd args as dict

#replace short arg name with long one
for arg in list(args.keys()):
    for sh_arg in ValidArgs:
        if arg == sh_arg.short:
            args[sh_arg.name] = args.pop(arg)

config = configparser.ConfigParser()

config_file = args.get(ValidArgs.config_location.name, ValidArgs.config_location.default) # if config file position is given use that, if not, use default
successfull_reads = config.read(
    config_file
)
if not successfull_reads:
    raise FileNotFoundError(f"Failed to read config file(s): {config_file}")

# get important folder paths and associate them with their name
folders = {
    folder_type.name: args.get(folder_type.name, folder_type.default)
    for folder_type in ValidArgs
    if folder_type.arg_type == "folder"
}

# make folders if they don't exist yet
for folder in folders.values():
    os.makedirs(folder, exist_ok=True)

