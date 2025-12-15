# Filter Type imports
from filter_types.filter_type import FilterType
from filter_types.filter_types import register_ft

# src modules imports
from Errors import MEM
from logger import logger

# builtin imports
from pathlib import Path
from typing import Union
from datetime import datetime

# library imports
from PIL import Image
import pillow_heif

@register_ft("datetime")
class DateTime(FilterType):
    def __init__(self, args:dict) -> None:
        self.TYPE = "datetime"
        logger.debug("validating datetime filter configuration")
        with MEM.branch("validating datetime filter configuration"):

            if args.get("start"):
                start_dt = args["start"]
            else:
                MEM.queue_error("couldn't validate datetime filter configuration",
                                "start argument is missing")
                return
            
            if args.get("end"):
                end_dt = args["end"]
            else:
                MEM.queue_error("couldn't validate datetime filter configuration",
                                "end argument is missing")
                return
            
            valid = True

            if isinstance(start_dt, list) and isinstance(end_dt, list):
                logger.debug("using multiple start and end datetimes")
                
                logger.debug("validating start datetime types")
                invalid_datetimes:list[int] = []
                all_dt = True
                for i, st in enumerate(start_dt):
                    if not isinstance(st, datetime):
                        invalid_datetimes.append(i)
                        all_dt = False
                if all_dt == False:
                    MEM.queue_error("found invalid datetime syntax in datetime list", 
                                    f"the following indexes in the start datetime list have invalid syntax:\n{invalid_datetimes}")
                    valid = False
                
                logger.debug("validating end datetime types")
                invalid_datetimes:list[int] = []
                all_dt = True
                for i, et in enumerate(end_dt):
                    if not isinstance(et, datetime):
                        invalid_datetimes.append(i)
                        all_dt = False
                if all_dt == False:
                    MEM.queue_error("found invalid datetime syntax in datetime list", 
                                    f"the following indexes in the end datetime list have invalid syntax:\n{invalid_datetimes}")
                    valid = False
                del all_dt, invalid_datetimes

                logger.debug("checking if both lists are the same length")
                if len(start_dt) != len(end_dt):
                    MEM.queue_error("couldn't validate datetimes",
                                    "start list and end list are different lengths")
                    valid = False

                if valid:
                    logger.debug("lists valid so far, checking that start datetimes are before end datetimes")
                    startdt:list[datetime] = start_dt
                    enddt:list[datetime] = end_dt

                    invalid_indexes:list[int] = []
                    for i, (st, et) in enumerate(zip(startdt, enddt)):
                        if not (st < et):
                            invalid_indexes.append(i)
                            valid = False
                    if not valid:
                        MEM.queue_error("found invalid datetime combinations",
                                        f"the start datetime is after the end datetime at the following indexes:\n{invalid_indexes}")
                    del invalid_indexes
                    if valid:
                        self.start_dt:Union[datetime, list[datetime]] = startdt
                        self.end_dt:Union[datetime, list[datetime]] = enddt


            elif isinstance(start_dt, list) != isinstance(end_dt, list):
                MEM.queue_error("could not validate datetimes","only start or only end is a list")
                valid = False


            elif isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
                logger.debug("using single start and end datetimes")
                sdt: datetime = start_dt
                edt: datetime = end_dt
                if not (sdt < edt):
                    valid = False
                    MEM.queue_error("found invalid datetime combination",
                                    "the start datetime is after the end datetime")
                if valid:
                    self.start_dt:Union[datetime, list[datetime]] = sdt
                    self.end_dt:Union[datetime, list[datetime]] = edt
            
            #self.valid = valid
                

            
    async def filter(self, image:Path, sn:str) -> bool:
        pillow_heif.register_heif_opener() # support heif
        img = Image.open(image)
        exif = img.getexif()
        raw = exif.get(306)  # "2024:11:29 15:23:10"
        if raw is None:
            logger.warning(f"{image} does not have date and time metadata, skipping")
            return False
        else:
            dt = datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
        
        if isinstance(self.start_dt, datetime) and isinstance(self.end_dt, datetime):
            if self.start_dt < dt < self.end_dt:
                return True
            return False
        elif isinstance(self.start_dt, list) and isinstance(self.end_dt, list):
            for st, et in zip(self.start_dt, self.end_dt):
                if st < dt < et:
                    return True
            return False
        else:
            logger.critical("what the fuck, this is not normal, you are a magician or something, lets just ignore this for now :')")
            return False