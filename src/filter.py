from filter_types.filter_types import FilterTypes, FilterType
from filter_types.filter_arg_types.filter_arg_type import FilterArgType

from typing import Type


class Filter():
    """class that, when instantiated, contains all information about a specific filter defined in the configuration"""
    def __init__(self, filter_name: str, filter_type_name:str) -> None:
        self.filter_name = filter_name

        self.filter_type:FilterTypes = FilterTypes[filter_name]
        
    
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