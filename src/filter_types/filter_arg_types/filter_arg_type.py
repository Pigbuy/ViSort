
class FilterArgType():
    """A filter argument type is an argument type that is used by a filter/filter type.
    It can validate and parse that type from text in the configuration file and can then be used by the filter type
    to parse its arguments which may be multiple of different types. This type of class may be instantiated for ease of use."""
    @staticmethod
    def validate_str(string:str) -> bool:
        """returns False if the string is not valid, True if it is valid"""
        return True
    @staticmethod
    def from_valid_str(valid_string: str) -> "FilterArgType":
        return FilterArgType(valid_string)
    def __init__(self, input) -> None:
        self.input = input