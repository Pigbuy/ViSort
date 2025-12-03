from filter_types.filter_type import FilterType
from filter_arg_types.coordinates import Coordinates

class Coords(FilterType):
    def __init__(self, coords: str, radius: int) -> None:
        self.coords = coords
        self.radius = radius

    def filter(self, image) -> bool:
        pass