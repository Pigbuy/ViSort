# arg type imports
import json
from filter_types.filter_arg_types.location import Location
from filter_types.filter_arg_types.interval import Interval

# Filter Type imports
from filter_types.filter_type import FilterType
from filter_types.filter_types import register_ft

# src modules imports
from Errors import MEM
from logger import logger

# builtin imports
from pathlib import Path
from typing import Optional, Union, cast

# library imports
from PIL import Image
import pillow_heif

@register_ft("location")
class Loc(FilterType):
    def __init__(self, args:dict) -> None:
        self.TYPE = "datetime"
        logger.debug("validating location filter configuration")
        with MEM.branch("validating location filter configuration"):
            if args.get("location"):
                location = args["location"]
            else:
                MEM.queue_error("could not validate location filter configuration",
                                "location argument is missing")
                return
            
            if args.get("radius"):
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
                MEM.queue_error("could not validate location filter configuration",
                                f"location argument is not a string or list of strings.\nInstead it's: {type(location).__name__}")

            if isinstance(radius, (float, int)) or radius is None:
                self.radius:Optional[Union[float,int, Interval]] = radius
            elif isinstance(radius, str):
                self.radius:Optional[Union[float,int, Interval]] = Interval(radius)
            else:
                MEM.queue_error("could not validate location filter configuration",
                                f"radius argument is not an integer, float, string(interval) or nothing.\nInstead it's: {type(radius).__name__}")
                

            caching = args.get("caching")
            if caching:
                if isinstance(caching, bool):
                    self.caching = caching
                else:
                    MEM.queue_error("could not validate location filter configuration",
                                    f"caching argument is not an a boolean or empty.\nInstead it's: {type(caching).__name__}")
            else:
                self.caching = True
    
    async def filter(self, image: Path) -> bool:
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
                    except:
                        pass
                    
                    logger.warning(f"no location metadata found in:{image_path}")
                    return None

            except:
                logger.warning(f"could not read file '{image_path}' to get location metadata")
                return None
        
        image_coords = extract_coords(image)
        if image_coords is None:
            return False


        def in_radius(loc:Location) -> bool:
            if self.radius and (isinstance(self.radius, (float, int))):
                return loc.get_dist_to_km(image_coords) <= self.radius
            elif self.radius and isinstance(self.radius, Interval):
                return self.radius.contains(loc.get_dist_to_km(image_coords))
            else:
                return False
        

        if self.caching:
            img = Image.open(image)
            exif = img.getexif()
            description = exif.get(0x010E)

            if description:
                try:
                    j = json.loads(description)
                except:
                    j = None
                
                if j:
                    if j.get("description"):
                        # if location is fully cached
                        logger.info(f"using cached location for {image}")
                        loc = j
                        if isinstance(self.location, Location):
                            r = self.location.is_loc_in_same_smallest_region(loc=loc)
                            if r or in_radius(self.location):
                                return True
                            return False
                        else:
                            for l in self.location:
                                r = l.is_loc_in_same_smallest_region(loc=loc)
                                if r or in_radius(l):
                                    return True
                            return False
                    # if description json was found but no location entry
                    else:
                        logger.info(f"making new location cache entry for {image}")
                        if isinstance(self.location, Location):
                            loc = await Location.get_loc_from_coords(image_coords)
                            jayson = j
                            jayson["location"] = loc
                            exif[0x010E] = json.dumps(jayson).encode()
                            img.save(image,exif=exif)
                            r = self.location.is_loc_in_same_smallest_region(loc= cast(dict, loc))
                            if r or in_radius(self.location):
                                return True
                            return False
                        else:
                            for l in self.location:
                                loc = await Location.get_loc_from_coords(image_coords)
                                jayson = j
                                jayson["location"] = loc
                                exif[0x010E] = json.dumps(jayson).encode()
                                img.save(image,exif=exif)
                                r = l.is_loc_in_same_smallest_region(loc= cast(dict, loc))
                                if r or in_radius(l):
                                    return True
                            return False


            # if no description or cached location was found
            else:
                logger.info(f"making new cache json with location entry for {image}")
                if isinstance(self.location, Location):
                    loc = await Location.get_loc_from_coords(image_coords)
                    jayson = {"location": loc}
                    exif[0x010E] = json.dumps(jayson).encode()
                    img.save(image,exif=exif)
                    r = self.location.is_loc_in_same_smallest_region(loc= cast(dict, loc))
                    if r or in_radius(self.location):
                        return True
                    return False
                else:
                    for l in self.location:
                        loc = await Location.get_loc_from_coords(image_coords)
                        jayson = {"location": loc}
                        exif[0x010E] = json.dumps(jayson).encode()
                        img.save(image,exif=exif)
                        r = l.is_loc_in_same_smallest_region(loc= cast(dict, loc))
                        if r or in_radius(l):
                            return True
                    return False
        

        # if caching is disabled
        else:
            if isinstance(self.location, Location):
                r = await self.location.are_coords_in_same_smallest_region(image_coords)
                if r or in_radius(self.location):
                    return True
                return False
            else:
                for l in self.location:
                    r = await l.are_coords_in_same_smallest_region(image_coords)
                    if r or in_radius(l):
                        return True
                return False
        
        return False #pylance likes this even tho its unreachable