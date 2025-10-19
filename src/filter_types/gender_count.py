from filter_types.filter_type import FilterType
class GenderCount(FilterType):
    def __init__(self, male_count: int, female_count: int) -> None:
        self.male_count = male_count
        self.female_count = female_count

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass