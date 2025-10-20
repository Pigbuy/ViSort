from enum import Enum
from typing import Type

from filter_types.filter_arg_types.filter_arg_type import FilterArgType

class FilterType():
    class Args(Enum):
        pass
        def __init__(self, arg_type: Type) -> None:
            self.arg_type: Type[FilterArgType] = arg_type

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def validate_str_args() -> str: return ""
    def filter(self, image) -> bool: return True