from filter_types.filter_type import FilterType
class Description(FilterType):
    def __init__(self, desc: str) -> None:
        self.desc = desc

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass