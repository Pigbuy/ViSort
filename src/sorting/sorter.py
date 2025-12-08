from pathlib import Path
from logger import logger
from Errors import MEM
from filter_group import FilterGroup


class Sorter:
    """A Sorter defines how and where images matching filters should be organized"""
    
    def __init__(self, name: str, config: dict) -> None:
        logger.debug(f"validating {name} Sorter")
        with MEM.branch(f"validating {name} Sorter"):
            self.name = name
            
            # validate and parse priority
            priority = config.get("priority")
            if priority is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: priority")
            elif not isinstance(priority, int):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter priority must be an integer, not {type(priority).__name__}")
            else:
                self.priority: int = priority
            
            # validate and parse method
            method = config.get("method")
            valid_methods = {"move", "link", "tag", "name", "json"}
            if method is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: method")
            elif not isinstance(method, str):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter method must be a string, not {type(method).__name__}")
            elif method not in valid_methods:
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter method '{method}' is not valid. Valid methods are: {', '.join(valid_methods)}")
            else:
                self.method: str = method
            
            # validate and parse input_folder
            input_folder = config.get("input_folder")
            if input_folder is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: input_folder")
            elif not isinstance(input_folder, str):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter input_folder must be a string, not {type(input_folder).__name__}")
            else:
                self.input_folder: Path = Path(input_folder)
            
            # validate and parse output_folder
            output_folder = config.get("output_folder")
            if output_folder is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: output_folder")
            elif not isinstance(output_folder, str):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter output_folder must be a string, not {type(output_folder).__name__}")
            else:
                self.output_folder: Path = Path(output_folder)
            
            # validate and parse resolve_equal_sort_method
            resolve_method = config.get("resolve_equal_sort_method")
            valid_resolve_methods = {"all", "auto", "filter_hierarchy", "group_hierarchy"}
            if resolve_method is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: resolve_equal_sort_method")
            elif not isinstance(resolve_method, str):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter resolve_equal_sort_method must be a string, not {type(resolve_method).__name__}")
            elif resolve_method not in valid_resolve_methods:
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter resolve_equal_sort_method '{resolve_method}' is not valid. Valid methods are: {', '.join(valid_resolve_methods)}")
            else:
                self.resolve_equal_sort_method: str = resolve_method
            
            # validate and parse hierarchy (optional, but required if resolve_equal_sort_method is hierarchy-based)
            hierarchy = config.get("hierarchy")
            if hierarchy is None:
                if resolve_method and resolve_method != "auto":
                    MEM.queue_error("could not parse Sorter configuration",
                                    f"Sorter hierarchy is required when resolve_equal_sort_method is '{resolve_method}'")
            elif not isinstance(hierarchy, list):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter hierarchy must be a list, not {type(hierarchy).__name__}")
            else:
                self.hierarchy: list = hierarchy


    class SortingMethods:
        @staticmethod
        def move():
            pass
        @staticmethod
        def link():
            pass
        @staticmethod
        def tag():
            pass
        @staticmethod
        def name():
            pass
        @staticmethod
        def json():
            pass
    
    class ConflictHandlers:
        #@staticmethod
        #def auto(conform_fgs:list[FilterGroup]) -> list[FilterGroup]:
        #    pass
        @staticmethod
        def all(conform_fgs:list[FilterGroup]) -> list[FilterGroup]:
            return conform_fgs
        @staticmethod
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

        @staticmethod
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

            



    def sort(self):
        pass