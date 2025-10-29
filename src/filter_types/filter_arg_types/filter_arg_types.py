from typing import Type, Dict, Callable

from filter_types.filter_arg_types.filter_arg_type import FilterArgType

# Runtime registry for FilterArgType subclasses. Modules should call
# `register("name")(Cls)` (or use the decorator) to register arg types.
REGISTRY: Dict[str, Type[FilterArgType]] = {}

def register(name: str) -> Callable[[Type[FilterArgType]], Type[FilterArgType]]:
    def decorator(cls: Type[FilterArgType]) -> Type[FilterArgType]:
        REGISTRY[name] = cls
        return cls
    return decorator