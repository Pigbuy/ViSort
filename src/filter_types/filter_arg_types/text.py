from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from typing import Optional


class Text(FilterArgType):
    @staticmethod
    def validate_str(string: str) -> bool:
        """
        Validates if the input is a non-empty string.
        All non-empty strings are considered valid.
        """
        return isinstance(string, str) and len(string.strip()) > 0

    def parse_valid_string(self, valid_string: str) -> "Text":
        """
        Stores the validated string after stripping whitespace
        """
        self.text = valid_string.strip()
        return self

    def __init__(self, text: Optional[str] = None) -> None:
        """
        Initialize with an optional text string
        """
        self.text = text.strip() if text else None

    def __str__(self) -> str:
        """
        Returns the stored text
        """
        return self.text if self.text else ""