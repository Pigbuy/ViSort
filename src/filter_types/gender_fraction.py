from filter_types.filter_type import FilterType
class GenderFraction(FilterType):
    def __init__(self, male_frac: float, female_frac: float) -> None:
        self.male_frac = male_frac
        self.female_frac = female_frac

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass