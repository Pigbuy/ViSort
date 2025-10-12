from filter_types.filter_arg_types.location import Location
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geo_check")


l = Location().parse_valid_string(input())

#loc = geolocator.geocode(input(), addressdetails=True, exactly_one=True, language="en")
#loc_coords = (getattr(loc, 'latitude', None), getattr(loc, 'longitude', None))

print( l.are_coords_in_same_smallest_region((-75.259830, 99.761892)))