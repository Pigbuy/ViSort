from filter_types.filter_type import FilterType
from filter_types.filter_types import REGISTRY as FILTER_REGISTRY

class FilterGroup():
    """class that, when instantiated, contains multiple filters and the ability to sort an image according to these filters into a category or assign it to an attribute"""
    def __init__(self, name, filters: tuple[FilterType, ...]) -> None:
        self.name = name
        self.filters: tuple[FilterType, ...] = filters

    def eval_importance(self):
        pass

    def filter_all(self, image) -> bool:
        for f in self.filters:
            if not f.filter(image):
                return False
        return True