# arg type imports
from filter_types.filter_arg_types.coordinates import Coordinates
from filter_types.filter_arg_types.interval import Interval

# Filter Type imports
from filter_types.filter_type import FilterType
from filter_types.filter_types import register_ft

# src modules imports
from Errors import MEM
from logger import logger

# builtin imports
from pathlib import Path
from typing import Optional, Union

# library imports
from PIL import Image
import pillow_heif
from sorting.sorter import Sorter

@register_ft("coordinates")
class Coords(FilterType):
    def __init__(self, args:dict) -> None:
        self.TYPE = "coordinates"
        valid = True
        logger.debug("validating coordinates filter configuration")
        with MEM.branch("validating coordinates filter configuration"):
            coords = 0 #bind coords so type checker doesnt think its unbound
            if args.get("coords"):
                coords = args["coords"]
            else:
                MEM.queue_error("couldn't validate coordinates filter configuration",
                                "coords argument is missing")
                valid = False
            
            radius = 0
            if args.get("radius"):
                radius = args["radius"]
            else:
                MEM.queue_error("couldn't validate coordinates filter configuration",
                                "radius argument is missing")
                valid = False
            
            if not valid:
                return

            if isinstance(coords, str):
                self.coords:Union[Coordinates, list[Coordinates]] = Coordinates(coords)
            elif isinstance(coords, list):
                self.coords: Union[Coordinates, list[Coordinates]] = []
                for c in coords:
                    self.coords.append(Coordinates(c))
            else:
                MEM.queue_error("couldn't validate coordinates filter configuration",
                                f"coords argument isn't a string or a list of strings.\nInstead it's: {type(coords).__name__}")
            
            if isinstance(radius, (int, float)):
                self.radius = radius
            elif isinstance(radius, str):
                self.radius = Interval(radius)
            else:
                MEM.queue_error("couldn't validate coordinates filter configuration",
                                f"radius argument isn't an integer, float or str(interval).\nInstead it's: {type(radius).__name__}")

    async def filter(self, image:Path, sorter:Sorter) -> bool:
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
        
        def in_radius(coords:Coordinates) -> bool:
            if isinstance(self.radius, (float, int)):
                return coords.get_dist_to_km(image_coords) <= self.radius
            elif isinstance(self.radius, Interval):
                return self.radius.contains(coords.get_dist_to_km(image_coords))
            else:
                return False
        
        if isinstance(self.coords, list):
            for c in self.coords:
                if in_radius(c):
                    return True
            return False
        else:
            if in_radius(self.coords):
                return True
            return False
            

        