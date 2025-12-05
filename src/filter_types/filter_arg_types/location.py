from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy import distance
from Errors import MEM


geolocator = Nominatim(user_agent="geo_check")

class Location(FilterArgType):
    def __init__(self, string):
        if not isinstance(string, str):
            MEM.queue_error("could not validate location filter configuration",
                            f"location argument is not a list of strings.\nInstead the list contains: {type(string).__name__}")
        valid = True
        try:
            loc = geolocator.geocode(string, addressdetails=True, exactly_one=True, language="en")  # type: ignore[arg-type]
            if not loc:
                MEM.queue_error("Couldn't validate location",
                                "text in location field is garbage, wtf did you type in there? Try something else.")
                valid = False
                
        except GeocoderTimedOut:
            MEM.queue_error("Couldn't validate location",
                            "Geocoder timed out. Check your internet or check if osm/Nominatim are down")
            valid = False
        if valid:
            self.location = geolocator.geocode(valid_string, addressdetails=True, exactly_one=True, language="en")  # type: ignore[arg-type]
        else:
            self.location = "Ohio" #idk lol needed a default value, hope it doesn't break anything

    def are_coords_in_same_smallest_region(self, coords:tuple[float,float]) -> bool:
        """returns True if the given coordinates are in the same smallest specified region.
        For example if the location is \"Bergen, Norway\", and the coordinates are in Bergen it will return true.
        This works for countries, states, regions, municipalities, cities, towns, villages, suburbs, neighbourhoods, hamlets and localities"""
        addr = getattr(self.location, 'raw', {}).get('address', {})
        coord_addr = getattr(geolocator.reverse(coords, addressdetails=True, exactly_one=True, language="en"), 'raw', {}).get('address', {})  # type: ignore[arg-type]
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

    def get_dist_to_km(self, coords) -> float:
        self_coords = (getattr(self.location, 'latitude', None), getattr(self.location, 'longitude', None))
        return distance.distance(self_coords, coords).km