from filter_types.filter_type import FilterType, FilterArgType, Type, Enum
from filter_types.filter_arg_types.filter_arg_types import FilterArgTypes
from logger import logger
class TimeIntervals(FilterType):

    class Args(FilterType.Args, Enum):
        start_dt = FilterArgTypes.DateTime.arg_type
        end_dt = FilterArgTypes.DateTime.arg_type
        def __init__(self, arg_type: Type) -> None:
            self.arg_type: Type[FilterArgType] = arg_type

    def __init__(self, start_dt: str, end_dt:str) -> None:
        # split if multiple DateTimes are used
        self.start_dt, self.end_dt = start_dt.split(","), end_dt.split(",")
        


    def filter(self, image) -> bool:
        pass