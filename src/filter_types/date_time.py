from filter_types.filter_type import FilterType
from filter_types.filter_types import register

from datetime import datetime

from Errors import MEM
from logger import logger

@register("datetime")
class DateTime(FilterType):
    def __init__(self, start_dt, end_dt) -> None:
        logger.debug("validating datetime filter")
        with MEM.branch("validating datetime filter configuration"):
            valid = True

            if isinstance(start_dt, list) and isinstance(end_dt, list):
                logger.debug("using multiple start and end datetimes")
                self.multi = True
                
                logger.debug("validating start datetime types")
                invalid_datetimes:list[int] = []
                all_dt = True
                for i, st in enumerate(start_dt):
                    if not isinstance(st, datetime):
                        invalid_datetimes.append(i)
                        all_dt = False
                if all_dt == False:
                    MEM.queue_error("found invalid datetime syntax in start datetime list", 
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
                    MEM.queue_error("found invalid datetime syntax in end datetime list", 
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
                        self.start_dt = startdt
                        self.end_dt = enddt


            elif isinstance(start_dt, list) != isinstance(end_dt, list):
                MEM.queue_error("could not validate datetimes","only start or only end is a list")
                valid = False


            elif isinstance(start_dt, datetime) and isinstance(end_dt, datetime):
                logger.debug("using single start and end datetimes")
                self.multi = False
                sdt: datetime = start_dt
                edt: datetime = end_dt
                if not (sdt < edt):
                    valid = False
                    MEM.queue_error("found invalid datetime combination",
                                    "the start datetime is after the end datetime")
                if valid:
                    self.start_dt = sdt
                    self.end_dt = edt
                

            
    def filter(self, image) -> bool:
        return False