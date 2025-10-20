from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy import distance


geolocator = Nominatim(user_agent="geo_check")

class Location(FilterArgType):
    @staticmethod
    def validate_str(string:str) -> str:
        try:
            loc = geolocator.geocode(string, addressdetails=True, exactly_one=True, language="en")
            if not loc:
                return "Wth did you type in the location field lol. It's garbage. Try again"
        except GeocoderTimedOut:
            return "Timed out while geocoding, check your internet"
        return ""
        
    @staticmethod
    def from_valid_str(valid_string) -> "Location":
        return Location(geolocator.geocode(valid_string, addressdetails=True, exactly_one=True, language="en"))

    def are_coords_in_same_smallest_region(self, coords:tuple[float,float]) -> bool:
        addr = getattr(self.location, 'raw', {}).get('address', {})
        coord_addr = getattr(geolocator.reverse(coords, addressdetails=True, exactly_one=True, language="en"), 'raw', {}).get('address', {})
        print(addr)
        print(coord_addr)
        one_common = False
        for key in ['country', 'state', 'region', 'county', 'municipality', 'city', 'town', 'village', 'suburb', 'neighbourhood', 'hamlet', 'locality']:
            val1: str = addr.get(key, "").lower()
            val2: str = coord_addr.get(key, "").lower()

            if key in addr and key in coord_addr:
                one_common = True
                if val1 != val2:
                    return False
            # if both locations have no key in common return False
            else:
                if key == 'locality' and one_common == False:
                    return False
        
        return True

    def get_dist_to(self, coords) -> float:
        self_coords = (getattr(self.location, 'latitude', None), getattr(self.location, 'longitude', None))
        return distance.distance(self_coords, coords).km
    
    def __init__(self, location) -> None:
        self.location = location