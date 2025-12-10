from typing import Type, Callable
from filter_types.filter_type import FilterType

# Runtime registry for FilterType subclasses. Modules should call
# `register("name")(Cls)` to register filter types.
FILTER_TYPES: dict[str, Type[FilterType]] = {}

def register(name: str) -> Callable[[Type[FilterType]], Type[FilterType]]:
    def decorator(cls: Type[FilterType]) -> Type[FilterType]:
        FILTER_TYPES[name] = cls
        return cls
    return decorator

def get(name: str) -> Type[FilterType]:
    # Import all filter types to register them
    from . import location
    from . import date_time
    from . import coords
    #from . import people
    #from . import people_count
    #from . import known_people_count
    #from . import gender_count
    #from . import gender_fraction
    #from . import average_age
    #from . import descripion
    return FILTER_TYPES[name]

def exists(name:str) -> bool:
    # Import all filter types to register them
    from . import location
    from . import date_time
    from . import coords
    #from . import people
    #from . import people_count
    #from . import known_people_count
    #from . import gender_count
    #from . import gender_fraction
    #from . import average_age
    #from . import descripion
    return name in FILTER_TYPES.keys()

def get_registry_copy() -> dict[str, type[FilterType]]:
    from . import location
    from . import date_time
    from . import coords
    #from . import people
    #from . import people_count
    #from . import known_people_count
    #from . import gender_count
    #from . import gender_fraction
    #from . import average_age
    #from . import descripion
    return FILTER_TYPES.copy()