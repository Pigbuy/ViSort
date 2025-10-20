from enum import Enum
from typing import Type

from filter_types.filter_type import FilterType
from filter_types.average_age import AverageAge
from filter_types.coords import Coords
from filter_types.time_intervals import TimeIntervals
from filter_types.descripion import Description
from filter_types.gender_count import GenderCount
from filter_types.gender_fraction import GenderFraction
from filter_types.known_people_count import KnownPeopleCount
from filter_types.location import Location
from filter_types.people_count import PeopleCount
from filter_types.people import People


class FilterTypes(Enum):
    location = Location
    coords = Coords
    desc = Description
    date = TimeIntervals
    people = People
    people_count = PeopleCount
    known_people_count = KnownPeopleCount
    average_age = AverageAge
    gender_count = GenderCount
    gender_fraction = GenderFraction

    def __init__(self, filter_type: Type) -> None:
        self.filter_type: Type[FilterType] = filter_type
