from pathlib import Path
import typing
from Errors import MEM
from logger import logger
from filter_types.filter_type import FilterType
from filter_types.filter_types import get, exists
from typing import Union

class FilterGroup():
    """class that, when instantiated, contains multiple filters and the ability to sort an image according to these filters into a category or assign it to an attribute"""
    def __init__(self, name:str, filters:dict) -> None:
        logger.debug(f"validating \"{name}\" FilterGroup")
        with MEM.branch(f"validating \"{name}\" FilterGroup"):
            self.name = name
            self.filters:list[FilterType] = []

            for f_type, args in filters.items():
                if exists(f_type):
                    Ft = get(f_type)
                    if isinstance(args, dict):
                        self.filters.append(Ft(args))
                    else:
                        MEM.queue_error("could not parse Filter",
                                        f"Filter does not have arguments. Instead its an object of the following type: {type(args).__name__}")
                else:
                    MEM.queue_error("could not parse Filter",
                                    f"Filter Type \"{f_type}\" doesn't exist")

    def filter_all(self, image:Path) -> bool:
        for f in self.filters:
            if not f.filter(image):
                return False
        return True