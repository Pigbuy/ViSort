import time
import os
from typing import cast
import requests
import asyncio
import aiohttp
from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from geopy import distance
from Errors import MEM
from logger import logger
from cli_args import args

LOCATIONIQ_KEY = args.locationiq_key#os.environ.get("LOCATIONIQ_KEY")
BASE_FWD = "https://eu1.locationiq.com/v1/search"
BASE_REV = "https://eu1.locationiq.com/v1/reverse"


def safe_geocode(q: str | tuple[float, float], retries: int = 5):
    def is_LocationIQ_Error(r:(dict | list), i:int) -> bool:
        if isinstance(r, list):
            return False
        match r.get("error"):
            case None:
                return False
            case "Invalid Request":
                raise Exception("For some reason the LocationIQ request is invalid. This program will probably have to be updated before it works again.")
            case "Invalid Key":
                raise Exception("Your LocationIQ Key is invalid")
            case "Access restricted":
                raise Exception("Access to LocationIQ is restricted for some reason")
            case "Unable to geocode":
                pass
            case "Rate Limited Day":
                raise Exception("You have been rate limited for the day by LocationIQ")
            case "Rate Limited Minute":
                logger.warning("waiting 30 seconds because LocationIQ rate limited you for this minute")
                time.sleep(30)
            case "Rate Limited Second":
                logger.info("waiting half a second because LocationIQ rate limited you")
                time.sleep(0.5)
            case "Unknown error - Please try again after some time":
                if i <= 3:
                    logger.warning("LocationIQ ran into an unknown error sooo Im gonna try again in a second")
                    time.sleep(1)
                else:
                    raise Exception("LocationIQ is having problems atm, you'll have to wait until its fixed")
            case _:
                raise Exception("an unknown error occured while geocoding a location")
        return True
    
    for i in range(retries):
        if isinstance(q, str):
            r = requests.get(
                BASE_FWD,
                params={
                    "key": LOCATIONIQ_KEY,
                    "q": q,
                    "accept-language": "en",
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                    "normalizeaddress": 1,
                    "normalizecity": 1,
                },
                timeout=5,
            )
            data = r.json()
            if is_LocationIQ_Error(data, i):
                continue
            return data[0] if isinstance(data, list) and data else None

        else:  # reverse geocoding
            lat, lon = q
            r = requests.get(
                BASE_REV,
                params={
                    "key": LOCATIONIQ_KEY,
                    "lat": lat,
                    "lon": lon,
                    "accept-language": "en",
                    "format": "json",
                    "addressdetails": 1,
                    "normalizeaddress": 1,
                    "normalizecity": 1,
                    "oceans": 1
                },
                timeout=5,
            )
            data = r.json()
            if is_LocationIQ_Error(data, i):
                continue
            return data if isinstance(data, dict) else None
    return None

async def safe_geocode_async(q: str | tuple[float, float], retries: int = 5):
    async def is_LocationIQ_Error(r: dict | list, i: int) -> bool:
        if isinstance(r, list):
            return False

        match r.get("error"):
            case None:
                return False
            case "Invalid Request":
                raise Exception("LocationIQ request is invalid")
            case "Invalid Key":
                raise Exception("Your LocationIQ key is invalid")
            case "Access restricted":
                raise Exception("Access to LocationIQ is restricted")
            case "Unable to geocode":
                pass
            case "Rate Limited Day":
                raise Exception("Rate limited for the day")
            case "Rate Limited Minute":
                logger.warning("Rate limited per minute, sleeping 30s")
                await asyncio.sleep(30)
            case "Rate Limited Second":
                logger.info("Rate limited per second, sleeping 0.5s")
                await asyncio.sleep(0.5)
            case "Unknown error - Please try again after some time":
                if i <= 3:
                    logger.warning("Unknown error, retrying")
                    await asyncio.sleep(1)
                else:
                    raise Exception("LocationIQ is currently unstable")
            case _:
                raise Exception("Unknown LocationIQ error")

        return True

    timeout = aiohttp.ClientTimeout(total=5)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for i in range(retries):
            try:
                if isinstance(q, str):
                    async with session.get(
                        BASE_FWD,
                        params={
                            "key": LOCATIONIQ_KEY,
                            "q": q,
                            "accept-language": "en",
                            "format": "json",
                            "limit": 1,
                            "addressdetails": 1,
                            "normalizeaddress": 1,
                            "normalizecity": 1,
                        },
                    ) as r:
                        data = await r.json()

                else:
                    lat, lon = q
                    async with session.get(
                        BASE_REV,
                        params={
                            "key": LOCATIONIQ_KEY,
                            "lat": lat,
                            "lon": lon,
                            "accept-language": "en",
                            "format": "json",
                            "addressdetails": 1,
                            "normalizeaddress": 1,
                            "normalizecity": 1,
                            "oceans": 1,
                        },
                    ) as r:
                        data = await r.json()
                        

                if await is_LocationIQ_Error(data, i):
                    continue

                return data[0] if isinstance(data, list) else data

            except:
                await asyncio.sleep(1 + i)


    return None

class Location(FilterArgType):
    def __init__(self, string):
        if not isinstance(string, str):
            MEM.queue_error(
                "could not validate location filter configuration",
                f"location argument is not a string.\nInstead it's of type: {type(string).__name__}"
            )

        loc = safe_geocode(string)
        if not loc:
            MEM.queue_error(
                "Couldn't validate location",
                "LocationIQ returned no results, throttled you, or you don't have internet."
            )
        else:
            self.location:dict = loc

    async def are_coords_in_same_smallest_region(self, coords: tuple[float, float]) -> bool:
        addr = self.location.get("address")
        coord = await safe_geocode_async(coords)
        coord_addr:dict = coord.get("address", {}) if coord else {}

        keys = [
            "country", "state", "county", "city", "island", "suburb", "neighbourhood", "road", "house_number"
        ]

        one_common = False
        for key in keys:
            v1 = cast(dict[str,str],addr).get(key, "").lower()
            v2 = cast(dict[str,str],coord_addr).get(key, "").lower()

            if (v1 != "") and (v2 != ""):
                one_common = True
                if v1 != v2:
                    return False
            else:
                if key == keys[-1] and not one_common:
                    return False

        return True
    
    @staticmethod
    async def get_loc_from_coords(coords:tuple[float, float]):
        return safe_geocode(coords)


    def is_loc_in_same_smallest_region(self, loc:dict) -> bool:
        addr = self.location.get("address")
        coord = loc
        coord_addr:dict = coord.get("address", {}) if coord else {}

        keys = [
            "country", "state", "county", "city", "island", "suburb", "neighbourhood", "road", "house_number"
        ]

        one_common = False
        for key in keys:
            v1 = cast(dict[str,str],addr).get(key, "").lower()
            v2 = cast(dict[str,str],coord_addr).get(key, "").lower()

            if (v1 != "") and (v2 != ""):
                one_common = True
                if v1 != v2:
                    return False
            else:
                if key == keys[-1] and not one_common:
                    return False

        return True


    def get_coords(self) -> tuple[float, float]:
        lat = float(cast(str,self.location.get("lat")))
        lon = float(cast(str,self.location.get("lon")))
        return (lat,lon)

    def get_dist_to_km(self, coords: tuple[float, float]) -> float:
        return distance.distance(self.get_coords(), coords).km
