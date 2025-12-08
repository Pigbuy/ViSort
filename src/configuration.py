# Import src Modules
from typing import Optional
from filter_group import FilterGroup
from sorter import Sorter
from filter_types.filter_types import get, exists, get_registry_copy
from logger import logger
from Errors import MEM

# builtin imports
from pathlib import Path
import tomllib


class Configuration:
    def __init__(self, config_location:Path) -> None:
        with MEM.branch("reading configuration file"):
            with open(config_location, "rb") as f:
                config = tomllib.load(f)
            logger.debug("read config")

            fgs = config.get("FilterGroups")
            sts = config.get("Sorters")

            if not fgs:
                MEM.queue_error("could not validate configuration",
                                "you did not define any Filter Groups")
            elif not isinstance(fgs, dict):
                MEM.queue_error("could not validate configuration",
                                f"you put something of type {type(fgs).__name__} where you should define Filter Groups")

            if not sts:
                MEM.queue_error("could not validate configuration",
                                "you did not define any Sorters")
            elif not isinstance(sts, dict):
                MEM.queue_error("could not validate configuration",
                                f"you put something of type {type(fgs).__name__} where you should define the Sorters")

            MEM.throw_if_errors() # if any of the above was true throw the errors


            with MEM.branch("validating Filter Groups"):
                self.filter_groups:list[FilterGroup] = []
                if isinstance(fgs, dict):
                    for fgn, fg in fgs.items():
                        if isinstance(fg, dict):
                            self.filter_groups.append(FilterGroup(fgn, fg))
                        else:
                            MEM.queue_error("Could not validate Filter Group configuration",
                                            f"Filter Group {fgn} is not a dict with subitems but an item of the following type: {type(fg).__name__}")
                else:
                    MEM.queue_error("confusius maximus",
                                    "I just checked if Filter Groups is a dict and it was but now it isnt wtf")
            
            with MEM.branch("validating Sorters"):
                self.sorters:list[Sorter] = []
                if isinstance(sts, dict):
                    for sn, s in sts.items():
                        if isinstance(s, dict):
                            self.sorters.append(Sorter(sn, s))
                        else:
                            MEM.queue_error("Could not validate Sorter configuration",
                                            f"Sorter {sn} is not a dict with subitems but an item of the following type: {type(s).__name__}")
                else:
                    MEM.queue_error("confusius maximus",
                                    "I just checked if Sorters is a dict and it was but now it isnt wtf")
                    
            MEM.throw_if_errors()# if everything was parsed fine it will continue, if not it will throw errors

            with MEM.branch("validating used Sorters"):
                sorter_names = [s.name for s in self.sorters] 
                for fg in self.filter_groups:
                    if isinstance(fg.sorter, str):
                        if not (fg.sorter in sorter_names):
                            MEM.queue_error("could not validate all used sorters",
                                            f"Sorter \"{fg.sorter}\" does not exist, but was given as sorter in the \"{fg.name}\" Filter Group")
                    elif isinstance(fg.sorter, list):
                        for i, s in enumerate(fg.sorter):
                            if isinstance(s, str):
                                if not (s in sorter_names):
                                     MEM.queue_error("could not validate all used sorters",
                                            f"Sorter \"{s}\" does not exist, but was given as sorter in the \"{fg.name}\" Filter Group")
                            else:
                                MEM.queue_error("could not validate all used sorters",
                                                f"the element at index {i} in the sorter list of the Filter Group \"{fg}\" is not a string but of the following type: {type(s).__name__}")

            
            with MEM.branch("validating Sorter hierarchy"):
                for s in self.sorters:
                    fg_names = [fg.name for fg in self.filter_groups if fg.sorter == s.name or (isinstance(fg.sorter, list) and s.name in fg.sorter)]
                    if s.resolve_equal_sort_method == "fiter_hierarchy":
                        fr = get_registry_copy()
                        for f in s.hierarchy:
                            if f in fr.keys():
                                fr.pop(f)
                            else:
                                MEM.queue_error("could not validate filter hierarchy",
                                                f"Filter \"{f}\" does not exist")
                        if len(fr) > 0:
                            MEM.queue_error("could not validate filter hierarchy",
                                            f"not all filters were listed in the hierarchy.\nMissing Filters: {fr}")
                    
                    elif s.resolve_equal_sort_method == "group_hierarchy":
                        for g in s.hierarchy:
                            if g in fg_names:
                                fg_names.remove(g)
                            else:
                                MEM.queue_error("could not validate Group hierarchy",
                                                f"\"{g}\" is not a Filter Group using the \"{s}\" sorter")

            MEM.throw_if_errors()