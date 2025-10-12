from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from typing import Optional


class Text(FilterArgType):
    @staticmethod
    def validate_str(string: str) -> bool:
        return isinstance(string, str) and len(string.strip()) > 0

    def parse_valid_string(self, valid_string: str) -> "Text":
        self.text = valid_string.strip()
        return self

    def __init__(self, text: Optional[str] = None) -> None:
        self.text = text.strip() if text else None