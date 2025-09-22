import argparse
import configparser
from lists import ValidArgs

args = vars(argparse.ArgumentParser().parse_args()) #read cmd args as dict

#replace short arg name with long one
for arg in list(args.keys()):
    for sh_arg in ValidArgs:
        if arg == sh_arg.short:
            args[sh_arg.name] = args.pop(arg)

config = configparser.ConfigParser() # parse

config_file = args.get(ValidArgs.config_location.name, ValidArgs.config_location.default) # if config file position is given use that, if not, use default
successfull_reads = config.read(
    config_file
)
if not successfull_reads:
    raise FileNotFoundError(f"Failed to read config file(s): {config_file}")



