from filter_types.filter_types import REGISTRY as FILTER_REGISTRY
from filter_types.filter_arg_types.filter_arg_type import FilterArgType

from typing import Type


class Filter():
    """class that, when instantiated, contains all information about a specific filter defined in the configuration"""
    def __init__(self, filter_name: str, filter_type_name:str) -> None:
        self.filter_name = filter_name

        # filter types are registered in the runtime registry under a string key
        self.filter_type = FILTER_REGISTRY[filter_type_name]
        

    def filter(self, img) -> bool:
        return False
    

class FilterGroup():
    """class that, when instantiated, contains multiple filters and the ability to sort an image according to these filters into a category or assign it to an attribute"""
    def __init__(self, name, filters:tuple[Filter]) -> None:
        self.name = name
        self.filters = filters


class Category(FilterGroup):
    pass


class Attribute(FilterGroup):
    pass