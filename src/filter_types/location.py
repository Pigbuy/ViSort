# arg type imports
import asyncio
import json
from filter_types.filter_arg_types.location import Location
from filter_types.filter_arg_types.interval import Interval

# Filter Type imports
from filter_types.filter_type import FilterType
from filter_types.filter_types import register_ft

# src modules imports
from Errors import MEM
from logger import logger
from progress import event_queue

# builtin imports
from pathlib import Path
from typing import Optional, Union, cast

# library imports
from PIL import Image
import pillow_heif
from sorting.sorter import Sorter

locations_taken_care_of:dict[Sorter, dict[Path, dict | None]] = {}

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
    
    async def filter(self, image: Path, sorter:Sorter) -> bool:
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

        def get_loc_from_json_desc_metadata(image_path:Path) -> dict | int:
            pil_img = Image.open(image_path)
            exif = pil_img.getexif()
            desc = exif.get(0x010E)
            if desc:
                try:
                    desc = json.loads(desc)
                except:
                    return 2#"No json in description metadata"
            else:
                return 1#"No description metadata"

            #json is in the description exif metadata
            if isinstance(desc, dict):
                loc = desc.get("location")
                if loc:
                    return loc
                else:
                    return 0#"no location in json"
            #means the json isn't a dict
            return 3
        
        def write_cache(loc:dict, image_path:Path):
            pil_img = Image.open(image_path)
            exif = pil_img.getexif()
            match get_loc_from_json_desc_metadata(image_path):
                case 0:
                    exif_description_json = json.loads( cast ( str, exif.get(0x010E) ) )
                    exif_description_json["location"] = loc
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case 1:
                    exif_description_json = {"location": loc}
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case 2:
                    exif_description_json = {"location": loc, "old": exif.get(0x010E)}
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case 3:
                    exif_description_json = {"location": loc}
                    exif[0x010E] = json.dumps(exif_description_json).encode()
                    pil_img.save(image_path,exif=exif)
                case _:
                    pass
        
        image_coords = extract_coords(image)
        if image_coords is None:
            await event_queue.put({"type": "message", "sorter": sorter.name,"message": f"image does not have coordinates in its metadata: {image}"})
            return False

        def in_radius(loc:Location) -> bool:
            if self.radius and (isinstance(self.radius, (float, int))):
                return loc.get_dist_to_km(image_coords) <= self.radius
            elif self.radius and isinstance(self.radius, Interval):
                return self.radius.contains(loc.get_dist_to_km(image_coords))
            else:
                return False

        if sorter not in locations_taken_care_of:
            locations_taken_care_of[sorter] = {}

        is_being_rgd = locations_taken_care_of[sorter].get(image, False)

        if is_being_rgd is None:
            await event_queue.put({"type": "message", "sorter": sorter.name,"message": f"waiting for other filters reverse geocoding request of {image}"})
            async def wait_for_res():
                while locations_taken_care_of[sorter][image] is None:
                    await asyncio.sleep(0.01)
                return locations_taken_care_of[sorter][image]
            location = await wait_for_res()
            await event_queue.put({"type": "message", "sorter": sorter.name,"message": f"got reverse geocoded location from other filter for {image}"})
        elif is_being_rgd is False:
            # telling other location filters to wait until I have location reverse geocoded so they can use it
            locations_taken_care_of[sorter][image] = None
            location = None
        else:
            # is_already_handled is already a valid location response from locationIQ
            await event_queue.put({"type": "message", "sorter": sorter.name,"message": f"got reverse geocoded location from other filter for {image}"})
            if is_being_rgd != True:
                location = is_being_rgd
            else:
                location = None

        # if allowed by config, check if theres a location cached in the image metadata
        if (not location) and self.caching:
            l = get_loc_from_json_desc_metadata(image)
            if not isinstance(l, int):
                await event_queue.put({"type": "message", "sorter": sorter.name,"message": f"got reverse geocoded location from image metadata location cache for {image}"})
                location = l
            else:
                location = None

        
        # if after all that, a location was found, use it
        if location:
            if not locations_taken_care_of[sorter].get(image):
                locations_taken_care_of[sorter][image] = location
            if isinstance(self.location, Location):
                r = self.location.is_loc_in_same_smallest_region(loc=location)
                if r or in_radius(self.location):
                    return True
                return False
            else:
                for l in self.location:
                    r = l.is_loc_in_same_smallest_region(loc=location)
                    if r or in_radius(l):
                        return True
                return False
         # if not it'll have to request the location from locationIQ after all
         # and here it doesn't cache it in the image metadata
        elif (not location) and (not self.caching):
            location = await Location.get_loc_from_coords(image_coords)
            locations_taken_care_of[sorter][image] = location
            await event_queue.put({"type": "message", "sorter": sorter.name,"message": f"got reverse geocoded location from a locationIQ request and made it available for other filters in sorter to use for {image}"})
            if isinstance(self.location, Location):
                r = self.location.is_loc_in_same_smallest_region(loc= cast(dict, location))
                if r or in_radius(self.location):
                    return True
                return False
            else:
                for l in self.location:
                    r = l.is_loc_in_same_smallest_region(loc= cast(dict, location))
                    if r or in_radius(l):
                        return True
                return False
         # and here it'll also cache the location in the image metadata
        else:
            location = await Location.get_loc_from_coords(image_coords)
            locations_taken_care_of[sorter][image] = location
            write_cache(cast(dict,location), image)
            await event_queue.put({"type": "message", "sorter": sorter.name,"message": f"got reverse geocoded location from a locationIQ request, made it available for other filters in sorter to use and cached it in the image metadata for {image}"})
            if isinstance(self.location, Location):
                r = self.location.is_loc_in_same_smallest_region(loc= cast(dict, location))
                if r or in_radius(self.location):
                    return True
                return False
            else:
                for l in self.location:
                    r = l.is_loc_in_same_smallest_region(loc= cast(dict, location))
                    if r or in_radius(l):
                        return True
                return False