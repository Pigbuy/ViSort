from filter_types.filter_type import FilterType
class PeopleCount(FilterType):
    def __init__(self, people_count: int) -> None:
        self.people_count = people_count

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass