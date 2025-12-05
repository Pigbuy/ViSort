# Import src Modules
from filter_types.filter_types import get, exists
from logger import logger
from Errors import MEM

# builtin imports
from pathlib import Path
import configparser
import tomllib

def get_and_validate_config(c_location:Path) -> configparser.ConfigParser:

    with open(c_location, "rb") as f:
        config = tomllib.load(f)
    logger.debug("read config")

    

#        for ft_name in config[category]["filter_type"]:
#            ft = FilterTypes[ft_name]


    # todo



    return config