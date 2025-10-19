from filter_types.filter_type import FilterType
class Location(FilterType):
    class FilterArgs():

    def __init__(self, country:str, city:str, address:str, radius:int) -> None:
        self.country = country
        self.city = city
        self.address = address
        self.radius = radius

    def validate(self) -> bool:
        pass
    def filter(self, image) -> bool:
        pass