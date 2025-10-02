from enum import Enum
from filter_types.filter_arg_types.coordinates import Coordinates
from filter_types.filter_arg_types.datetime import DateTime
from filter_types.filter_arg_types.interval import Interval
from filter_types.filter_arg_types.location import Location
from filter_types.filter_arg_types.text import Text

class FilterArgTypes(Enum):
    Coordinates
    DateTime
    Interval
    Location
    Text