from pathlib import Path
import configparser
import tomllib

from logger import logger
#from filter_types.filter_types import FilterTypes

def get_and_validate_config(c_location:Path) -> configparser.ConfigParser:

    with open(c_location, "rb") as f:
        config = tomllib.load(f)
    logger.debug("read config")

    #validate config
    logger.debug("validating config")
    if not config["Categories"]["categories"]:
        logger.critical(f'No section defining sorting categories in {c_location}')
        raise RuntimeError("Must specify list of categories in configuration file to sort the images into.")
    
    categories = [s.strip() for s in config["Categories"]["categories"].strip().split(",")]
    for category in categories:
        try:
            config[category]
        except KeyError:
            logger.critical(f'Did not configure \"{category}\" category')
            raise RuntimeError("Must configure every category")
        try:
            config[category]["filter_type"]
        except KeyError:
            logger.critical(f'Did not configure filter_type for category \"{category}\" ')
            raise RuntimeError("Must configure filter_type for every category")
        filter_types = [s.strip() for s in config[category]["filter_type"].strip().split(",")]
        if "coords" in filter_types and "location" in filter_types:
            logger.critical("Cannot use location and coords filter type in same category/Attribute configuration")
            raise RuntimeError("Cannot use location and coords filter type in same category/Attribute configuration")
        
#        for ft_name in config[category]["filter_type"]:
#            ft = FilterTypes[ft_name]
            
    
    # todo



    return config