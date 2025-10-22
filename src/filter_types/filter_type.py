from enum import Enum
from typing import Type

from filter_types.filter_arg_types.filter_arg_type import FilterArgType

class FilterType():
    class Args(Enum):
        pass
        @property
        def arg_type(self) -> Type[FilterArgType]:
            return self.value.arg_type

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def validate_str_args(argset: object) -> str:
        """Validate arguments for a filter. Default accepts any argset and returns empty error string.

        Individual filters can override this and use a specific ArgSet type.
        """
        return ""
    def filter(self, image) -> bool:
        """checks if the image complies with the filter"""
        return True