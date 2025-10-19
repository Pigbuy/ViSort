from filter_types.filter_type import FilterType
class People(FilterType):
    def __init__(self, people: str) -> None:
        self.people = people

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass