from typing import Type, Callable
from filter_types.filter_type import FilterType

# Runtime registry for FilterType subclasses. Modules should call
# `register("name")(Cls)` to register filter types.
REGISTRY: dict[str, Type[FilterType]] = {}

def register(name: str) -> Callable[[Type[FilterType]], Type[FilterType]]:
    def decorator(cls: Type[FilterType]) -> Type[FilterType]:
        REGISTRY[name] = cls
        return cls
    return decorator

def get(name: str) -> Type[FilterType]:
    return REGISTRY[name]

def exists(name:str) -> bool:
    return name in REGISTRY