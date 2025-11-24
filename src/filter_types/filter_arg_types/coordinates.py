from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from filter_types.filter_arg_types.filter_arg_types import register
from geopy import distance
from Errors import MEM

@register("coordinates")
class Coordinates(FilterArgType):
    @staticmethod
    def validate_str(string:str) -> bool:
        try:
            parts = string.split(',')
            if len(parts) != 2:
                MEM.queue_error("Couldn't validate coordinates",
                                "you didnt put in two numbers split with a comma")
                return False
            
            lat, lon = float(parts[0].strip()), float(parts[1].strip())
            if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                return True
            else: 
                MEM.queue_error("Couldn't validate coordinates",
                                "the coordinates values are out of bounds")
                return False
                
        except ValueError:
            MEM.queue_error("Couldn't validate coordinates",
                            "whatever you put before or after the comma isn't a number or cant be interpreted as a float")
            return False
                
    @staticmethod
    def from_valid_str(valid_string) -> "Coordinates":
        parts = valid_string.split(',')
        lat, lon = parts
        return Coordinates( ( float(lat.strip()), float(lon.strip()) ) )

    def get_dist_to(self, coordinates) -> float:
        return distance.distance(self.coordinates, coordinates).km

    def __init__(self, coordinates: tuple[float, float]) -> None:
        self.coordinates = coordinates
