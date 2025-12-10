import random as rand
from filter_group import FilterGroup

from typing import Callable, Any, Optional

HANDLERS: dict[str, Callable[..., Any]] = {}

def register_ch(name: Optional[str] = None):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        HANDLERS[name or func.__name__] = func
        return func
    return decorator

#@staticmethod
#def auto(conform_fgs:list[FilterGroup]) -> list[FilterGroup]:
#    pass

@register_ch("all")
def all(conform_fgs:list[FilterGroup], hierarchy:Optional[list[str]] = None) -> list[FilterGroup]:
    return conform_fgs

@register_ch("first")
def first(conform_fgs:list[FilterGroup], hierarchy:Optional[list[str]] = None) -> list[FilterGroup]:
    return [conform_fgs[0]]

@register_ch("random")
def random(conform_fgs:list[FilterGroup], hierarchy:Optional[list[str]] = None) -> list[FilterGroup]:
    index = rand.randrange(0, len(conform_fgs)-1)
    return [conform_fgs[index]]

@register_ch("filter_hierarchy")
def filter_hierarchy(conform_fgs:list[FilterGroup], hierarchy:list[str]) -> list[FilterGroup]:
    highest:FilterGroup = conform_fgs[0]
    highscore:int = 0
    max_score = len(hierarchy)
    for fg in conform_fgs:
        score: int = 0
        for f in fg.filters:
            score += max_score - hierarchy.index(f.TYPE)
        if score > highscore:
            highscore = score
            highest = fg
    return [highest]

@register_ch("group_hierarchy")
def group_hierarchy(conform_fgs:list[FilterGroup], hierarchy:list[str]) -> list[FilterGroup]:
    highest: FilterGroup = conform_fgs[0]
    highscore: int = 0
    max_score = len(hierarchy)
    for fg in conform_fgs:
        score: int = 0
        score = max_score - hierarchy.index(fg.name)
        if score > highscore:
            highest = fg
            highscore = score
    return [highest]

def handle_conflict(handler_name:str, conform_fgs:list[FilterGroup], hierarchy:list[str]):
    return HANDLERS[handler_name](conform_fgs=conform_fgs, hierarchy=hierarchy)