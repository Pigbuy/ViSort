from filter_arg_types.coordinates import Coordinates

from filter_types.filter_type import FilterType
from filter_types.filter_types import register

from Errors import MEM
from logger import logger

from pathlib import Path
from PIL import Image
from typing import Optional, Union

@register("coordinates")
class Coords(FilterType):
    def __init__(self, coords: Union[str, list[str]], radius: int) -> None:
        self.radius = radius
        with MEM.branch("validating coordinates filter configuration"):
            if isinstance(coords, str):
                self.coords:Union[Coordinates, list[Coordinates]] = Coordinates(coords)
            else:
                self.coords: Union[Coordinates, list[Coordinates]] = []
                for c in coords:
                    self.coords.append(Coordinates(c))

    def filter(self, image:Path) -> bool:
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
        
        if isinstance(self.coords, list):
            for c in self.coords:
                if c.get_dist_to_m(image_coords) <= self.radius:
                    return True
            return False
        else:
            if self.coords.get_dist_to_m(image_coords) <= self.radius:
                return True
            return False
            

        