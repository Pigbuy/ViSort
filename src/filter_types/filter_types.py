from enum import Enum
from filter_type import FilterType
from average_age import AverageAge
from coords import Coords
from date import Date
from descripion import Description
from gender_count import GenderCount
from gender_fraction import GenderFraction
from known_people_count import KnownPeopleCount
from location import Location
from people_count import PeopleCount
from people import People

from typing import Type

class FilterTypes(Enum):
    location = Location
    coords = Coords
    desc = Description
    date = Date
    people = People
    people_count = PeopleCount
    known_people_count = KnownPeopleCount
    average_age = AverageAge
    gender_count = GenderCount
    gender_fraction = GenderFraction

    def __init__(self, filter_type: Type) -> None:
        self.filter_type: Type[FilterType] = filter_type

FilterTypes["location"].filter_type