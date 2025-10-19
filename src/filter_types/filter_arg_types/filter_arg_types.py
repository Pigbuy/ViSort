from enum import Enum
from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from filter_types.filter_arg_types.coordinates import Coordinates
from filter_types.filter_arg_types.datetime import DateTime
from filter_types.filter_arg_types.interval import Interval
from filter_types.filter_arg_types.location import Location
from filter_types.filter_arg_types.text import Text
from filter_types.filter_arg_types.people import People

from typing import Type


class FilterArgTypes(Enum):
    Coordinates = Coordinates
    DateTime = DateTime
    Interval = Interval
    Location = Location
    Text = Text
    People = People

    def __init__(self, arg_type: Type) -> None:
            self.arg_type: Type[FilterArgType] = arg_type