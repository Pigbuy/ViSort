
class FilterArgType():
    @staticmethod
    def validate_str(string:str) -> str:
        return "" #return "" if valid, error mesage if not
    @staticmethod
    def from_valid_string(valid_string: str) -> "FilterArgType":
        return FilterArgType(valid_string)
    def __init__(self, input) -> None:
        self.input = input