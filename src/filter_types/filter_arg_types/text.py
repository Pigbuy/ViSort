from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from filter_types.filter_arg_types.filter_arg_types import register
from Errors import MEM


@register("text")
class Text(FilterArgType):
    @staticmethod
    def validate_str(string: str) -> bool:
        if isinstance(string, str) and len(string.strip()) > 0:
            return True
        else:
            MEM.queue_error("Text is not text",
                            "Either you forgot to put something there or you're not human and somehow changed the datatype of this argument into something that cannot be interpreted as text even though its in a text file")
            return False
    @staticmethod
    def from_valid_str(valid_string) -> "Text":
        return Text(valid_string.strip())

    def __init__(self, text: str) -> None:
        self.text = text.strip()