from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from geopy import distance


class Coordinates(FilterArgType):
    @staticmethod
    def validate_str(string:str) -> bool:
        try:
            parts = string.split(',')
            if len(parts) != 2:
                return False
            
            lat, lon = float(parts[0].strip()), float(parts[1].strip())
            return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
        except ValueError:
            return False

    def parse_valid_string(self, valid_string:str) -> None:
        parts = valid_string.split(',')
        lat, lon = parts
        self.coordinates = ( float(lat.strip()), float(lon.strip()) )

    def get_dist_to(self, coordinates) -> float:
        return distance.distance(self.coordinates, coordinates).km

    def __init__(self, coordinates:tuple[float, float]) -> None:
        self.coordinates = coordinates
