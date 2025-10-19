from filter_types.filter_type import FilterType
class AverageAge(FilterType):
    def __init__(self, average_age: int) -> None:
        self.average_age = average_age

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass