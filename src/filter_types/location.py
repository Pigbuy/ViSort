# arg type imports
from filter_arg_types.location import Location
from filter_arg_types.interval import Interval

# Filter Type imports
from filter_types.filter_type import FilterType
from filter_types.filter_types import register

# src modules imports
from Errors import MEM
from logger import logger

# builtin imports
from pathlib import Path
from typing import Optional, Union

# library imports
from PIL import Image
import pillow_heif

@register("location")
class Loc(FilterType):
    def __init__(self, args:dict) -> None:
        logger.debug("validating location filter configuration")
        with MEM.branch("validating location filter configuration"):
            if args["location"]:
                location = args["location"]
            else:
                MEM.queue_error("could not validate location filter configuration",
                                "lopcation argument is missing")
                return
            
            if args["radius"]:
                radius = args["radius"]
            else:
                radius = None

            if isinstance(location, str):
                self.location:Union[Location, list[Location]] = Location(location)
            elif isinstance(location, list):
                self.location:Union[Location, list[Location]] = []
                for l in location:
                    self.location.append(Location(l))
            else:
                MEM.queue_error("couldn't validate location filter configuration",
                                f"location argument is not a string or list of strings.\nInstead it's: {type(location).__name__}")

            if isinstance(radius, Optional[Union[float,int,str]]):
                self.radius:Optional[Union[float,int,str]] = radius
            else:
                MEM.queue_error("couldn't validate location filter configuration",
                                f"radius argument is not a number or string(interval).\nInstead it's: {type(radius).__name__}")
    
    def filter(self, image: Path) -> bool:
        pillow_heif.register_heif_opener() # support heif
        def extract_coords(image_path: Path) -> Optional[tuple[float, float]]:
            try:
                with Image.open(image_path) as img:
                    exif = img.getexif()

                    logger.debug(f"getting location metadata for {image_path}")
                    try:
                        gps_ifd = exif.get_ifd(34853)
                        if gps_ifd:
                            lat_dms = gps_ifd.get(2)
                            lat_ref = gps_ifd.get(1)
                            lon_dms = gps_ifd.get(4)
                            lon_ref = gps_ifd.get(3)

                            if lat_dms and lon_dms:
                                # Convert DMS (degrees, minutes, seconds) to decimal
                                lat = lat_dms[0] + lat_dms[1] / 60.0 + lat_dms[2] / 3600.0
                                lon = lon_dms[0] + lon_dms[1] / 60.0 + lon_dms[2] / 3600.0

                                # Apply reference directions
                                if isinstance(lat_ref, bytes):
                                    lat_ref = lat_ref.decode(errors="ignore")
                                if isinstance(lon_ref, bytes):
                                    lon_ref = lon_ref.decode(errors="ignore")

                                if str(lat_ref).upper().startswith("S"):
                                    lat = -abs(lat)
                                if str(lon_ref).upper().startswith("W"):
                                    lon = -abs(lon)

                                return (lat,lon)
                    except Exception:
                        pass
                    
                    logger.warning(f"no location metadata found in:{image_path}")
                    return None

            except Exception as e:
                logger.warning(f"could not read file {image_path}")
                return None
        
        image_coords = extract_coords(image)
        if image_coords is None:
            return False


        def in_radius(loc:Location) -> bool:
            if self.radius and (isinstance(self.radius, float) or isinstance(self.radius, int)):
                return loc.get_dist_to_km(image_coords) <= self.radius
            elif self.radius and isinstance(self.radius, str):
                i = Interval(self.radius)
                return i.contains(loc.get_dist_to_km(image_coords))
            else:
                return False

        if isinstance(self.location, Location):
            if self.location.are_coords_in_same_smallest_region(image_coords) or in_radius(self.location):
                return True
            return False
        else:
            for l in self.location:
                if l.are_coords_in_same_smallest_region(image_coords) or in_radius(l):
                    return True
            return False