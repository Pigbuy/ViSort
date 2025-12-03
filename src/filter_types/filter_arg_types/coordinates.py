from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from geopy import distance
from Errors import MEM

class Coordinates(FilterArgType):
    def __init__(self, string:str):
        #valid = True
        try:
            parts = string.split(',')
            if len(parts) != 2:
                MEM.queue_error("Couldn't validate coordinates",
                                "you didnt put in two numbers split with a comma")
                #valid = False
                lat, lon = 0.0 ,0.0
            else:
                lat, lon = float(parts[0].strip()), float(parts[1].strip())
                if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0): 
                    MEM.queue_error("Couldn't validate coordinates",
                                    "the coordinates values are out of bounds")
                    lat, lon = 0.0 ,0.0
                    #valid = False
                
        except ValueError:
            MEM.queue_error("Couldn't validate coordinates",
                            "whatever you put before or after the comma isn't a number or cant be interpreted as a float")
            lat, lon = 0.0 ,0.0
            #valid = False
        
        self.coordinates = (lat,lon)

    def get_dist_to(self, coordinates) -> float:
        return distance.distance(self.coordinates, coordinates).km