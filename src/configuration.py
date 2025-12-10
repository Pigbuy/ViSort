# Import src Modules
from typing import Optional, cast
from filter_group import FilterGroup
from sorting.sorter import Sorter
from filter_types.filter_types import get, exists, get_registry_copy
from logger import logger
from Errors import MEM

# builtin imports
from pathlib import Path
import tomllib


class Configuration:
    def __init__(self, config_location:Path) -> None:
        with MEM.branch("reading configuration file"):
            with open(config_location, "rb") as f:
                config = tomllib.load(f)
            logger.debug("read config")

            sts = config.get("Sorters")

            if not sts:
                MEM.queue_error("could not validate configuration",
                                "you did not define any Sorters")
            elif not isinstance(sts, dict):
                MEM.queue_error("could not validate configuration",
                                f"you put something of type {type(sts).__name__} where you should define the Sorters")

            MEM.throw_if_errors() # if any of the above was true throw the errors
            
            with MEM.branch("validating Sorters"):
                self.sorters:list[Sorter] = []
                for name, data in cast(dict, sts).items():
                    if isinstance(data, dict):
                        self.sorters.append(Sorter(name, data))
                    else:
                        MEM.queue_error("Could not validate Sorter configuration",
                                        f"Sorter {name} is not a dict with subitems but an item of the following type: {type(data).__name__}")
                    
            MEM.throw_if_errors()# if everything was parsed fine it will continue, if not it will throw errors