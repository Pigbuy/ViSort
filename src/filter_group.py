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

            if "sorter" not in filters.keys():
                MEM.queue_error("could not validate Filter Group",
                                f"the required \"sorter\" field is missing in the {name} Filter Group")
                

            for fname, args in filters.items():
                if exists(fname) and (fname != "sorter"):
                    Ft = get(fname)
                    if isinstance(args, dict):
                        self.filters.append(Ft(args))
                    else:
                        MEM.queue_error("could not parse Filter",
                                        f"Filter does not have arguments. Instead its an object of type: {type(args).__name__}")
                elif fname == "sorter":
                    if isinstance(args, (str, list)):
                        self.sorter:Union[str, list] = args
                    else:
                        MEM.queue_error("could not validate Filter Group",
                                        f"the \"sorter\" Filter Group attribute is not of type string or a list but of type {type(args).__name__}")
                else:
                    MEM.queue_error("could not parse Filter",
                                    f"Filter Type \"{fname}\" doesn't exist")

    def eval_importance(self):
        pass

    def filter_all(self, image) -> bool:
        for f in self.filters:
            if not f.filter(image):
                return False
        return True