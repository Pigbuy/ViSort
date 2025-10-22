from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from filter_types.filter_arg_types.filter_arg_types import register
from geopy import distance


@register("coordinates")
class Coordinates(FilterArgType):
    @staticmethod
    def validate_str(string:str) -> str:
        try:
            parts = string.split(',')
            if len(parts) != 2:
                return "coordinates not correctly formatted"
            
            lat, lon = float(parts[0].strip()), float(parts[1].strip())
            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                return ""
            else: 
                return "coordinates out of bounds"
        except ValueError:
            return "unexpected character in coordinates"
        
    @staticmethod
    def from_valid_str(valid_string) -> "Coordinates":
        parts = valid_string.split(',')
        lat, lon = parts
        return Coordinates( ( float(lat.strip()), float(lon.strip()) ) )

    def get_dist_to(self, coordinates) -> float:
        return distance.distance(self.coordinates, coordinates).km

    def __init__(self, coordinates: tuple[float, float]) -> None:
        self.coordinates = coordinates
