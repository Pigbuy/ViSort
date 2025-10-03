from main import args
from pathlib import Path
from filter_types.filter_arg_types.filter_arg_type import FilterArgType


class People(FilterArgType):
    @staticmethod
    def validate_str(string:str) -> bool:
        
    def parse_valid_string(self, valid_string) -> "FilterArgType":
        return self
    def __init__(self, people:tuple[str]) -> None:
        self.people = people