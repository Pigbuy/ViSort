from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
geolocator = Nominatim(user_agent="geo_check")

loc = geolocator.geocode("New York City, USA", addressdetails=True, exactly_one=True, language="en")

coords = (getattr(loc, 'latitude', None), getattr(loc, 'longitude', None))

print(coords)