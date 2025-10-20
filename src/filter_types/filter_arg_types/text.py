from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from typing import Optional


class Text(FilterArgType):
    @staticmethod
    def validate_str(string: str) -> str:
        if isinstance(string, str) and len(string.strip()) > 0:
            return ""
        else:
            return "how did you even get this error wtf"
    @staticmethod
    def from_valid_string(valid_string) -> "Text":
        return Text(valid_string.strip())

    def __init__(self, text: str) -> None:
        self.text = text.strip()