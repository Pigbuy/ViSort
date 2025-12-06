# Import src Modules
from filter_types.filter_types import get, exists
from logger import logger
from Errors import MEM

# builtin imports
from pathlib import Path
import configparser
import tomllib


class Configuration:
    def __init__(self, c_location:Path) -> None:
        with MEM.branch("reading configuration file"):
            with open(c_location, "rb") as f:
                config = tomllib.load(f)
            logger.debug("read config")

            if config["FilterGroups"]:
                self.filter_groups = config["FilterGroups"]
            else:
                MEM.add_error_reason("could not validate configuration",
                                "you did not define any Filter Groups")
            
            if config["Sorters"]:
                self.filter_groups = config["Sorters"]
            else:
                MEM.add_error_reason("could not validate configuration",
                                "you did not define any Sorters")

def get_and_validate_config(c_location:Path) -> configparser.ConfigParser:

    with open(c_location, "rb") as f:
        config = tomllib.load(f)
    logger.debug("read config")




    

#        for ft_name in config[category]["filter_type"]:
#            ft = FilterTypes[ft_name]


    # todo



    return config