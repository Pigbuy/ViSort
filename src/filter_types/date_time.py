from filter_types.filter_type import FilterType
from filter_types.filter_arg_types.filter_arg_types import REGISTRY as ARG_REGISTRY
from filter_types.filter_arg_types.datetime import DateTime as ArgDateTime

from logger import logger
from typing import cast, Protocol


class DateTimeLike(Protocol):
    dt: object
    def is_after(self, other: object) -> bool: ...


class DateTime(FilterType):

    class ArgSet():
        def __init__(self, start_dt: str, end_dt: str) -> None:
            self.start_dt = start_dt
            self.end_dt = end_dt


    def __init__(self, start_dt: str, end_dt:str) -> None:
        # split if multiple DateTimes are used
        sdts, edts = start_dt.split(","), end_dt.split(",")

        self.start_dt, self.end_dt = [], []
        dt_cls = ARG_REGISTRY["datetime"]
        for sdt, edt in zip(sdts, edts):
            s_obj = cast(ArgDateTime, dt_cls.from_valid_str(sdt))
            e_obj = cast(ArgDateTime, dt_cls.from_valid_str(edt))
            self.start_dt.append(s_obj)
            self.end_dt.append(e_obj)

    @staticmethod
    def validate_str_args(argset: object) -> str:
        # argset may be any object; access attributes dynamically to satisfy base signature
        sdts, edts = getattr(argset, 'start_dt').split(","), getattr(argset, 'end_dt').split(",")

        if len(sdts) != len(edts):
            return("there aren't the same amount of datetimes in start and end datetime arguments")
        else:
            err: list[str] = []
            dt_cls = ARG_REGISTRY["datetime"]
            for i, (sdt, edt) in enumerate(zip(sdts, edts)):
                err1 = dt_cls.validate_str(sdt)
                err2 = dt_cls.validate_str(edt)
                if err1 != "":
                    err.append(f'start_dt[{i}]: {err1}')
                if err2 != "":
                    err.append(f'end_dt[{i}]: {err2}')
                
                # narrow the returned FilterArgType to the concrete DateTime arg type
                s_obj = cast(DateTimeLike, dt_cls.from_valid_str(sdt))
                e_obj = cast(DateTimeLike, dt_cls.from_valid_str(edt))

                if s_obj.is_after(e_obj.dt):
                    err.append(f'start_dt[{i}] is after end_dt[{i}]')

            return str(err)



    def filter(self, image) -> bool:
        return False