from pathlib import Path
from queue import Queue
from logger import logger
from Errors import MEM
from filter_group import FilterGroup
import shutil
import os
from PIL import Image
import pillow_heif
import json

from filter_types.filter_types import get_registry_copy

from sorting.conflict_handlers import handle_conflict, HANDLERS
from sorting.sorting_methods import sort as actually_sort
from sorting.sorting_methods import SORTING_METHODS


class Sorter:
    """A Sorter defines how and where images matching filters should be organized"""

    def __init__(self, name: str, config: dict) -> None:
        logger.debug(f"validating {name} Sorter")
        with MEM.branch(f"validating {name} Sorter"):
            self.name = name
            self.queue:list[Path] = []
            
            # validate and parse priority
            priority = config.get("priority")
            if priority is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: priority")
            elif not isinstance(priority, int):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter priority must be an integer, not {type(priority).__name__}")
            elif isinstance(priority, int):
                self.priority: int = priority


            # validate and parse method
            method = config.get("method")
            if method is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: method")
            elif not isinstance(method, str):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter method must be a string, not {type(method).__name__}")
            elif method not in SORTING_METHODS:
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter method '{method}' is not valid.\nValid methods are: {', '.join(SORTING_METHODS)}")
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
                input_folder = Path(input_folder)
                if input_folder.exists():
                    if input_folder.is_dir():
                        self.input_folder: Path = input_folder
                    else:
                        MEM.queue_error("could not validate Sorter configuration",
                                        f"the specified input folder '{input_folder}' is not a folder")
            
                else:
                    MEM.queue_error("could not validate Sorter configuration",
                                    f"the specified input folder '{input_folder}' does not exist")
            

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
            if resolve_method is None:
                MEM.queue_error("could not parse Sorter configuration",
                                "Sorter is missing required field: resolve_equal_sort_method")
            elif not isinstance(resolve_method, str):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter resolve_equal_sort_method must be a string, not {type(resolve_method).__name__}")
            elif resolve_method not in HANDLERS:
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter resolve_equal_sort_method '{resolve_method}' is not valid.\nValid methods are: {', '.join(HANDLERS)}")
            else:
                self.resolve_equal_sort_method: str = resolve_method            

            with MEM.branch("validating Filter Groups"):
                self.filter_groups:list[FilterGroup] = []
                filter_groups = config.get("FilterGroups")
                if filter_groups is None:
                    MEM.queue_error("could not parse Filter Groups",
                                    f"there are no Filter Groups defined in the {self.name} Sorter")
                elif not isinstance(filter_groups, dict):
                    MEM.queue_error("could not parse Filter Groups",
                                    f"you put something of type {type(filter_groups).__name__} where you should define the Filter Groups")
                elif isinstance(filter_groups, dict):
                    for fg_name, fg_data in filter_groups.items():
                        if not isinstance(fg_data, dict):
                            MEM.queue_error("Could not validate Filter Group configuration",
                                            f"Filter Group {fg_name} is not a dict with subitems but an item of the following type: {type(fg_data).__name__}")
                        elif isinstance(fg_data, dict):
                            self.filter_groups.append(FilterGroup(fg_name, fg_data))


            # validate and parse hierarchy (optional, but required if resolve_equal_sort_method is hierarchy-based)
            hierarchy = config.get("hierarchy")
            if hierarchy is None:
                if resolve_method and resolve_method != "auto":
                    MEM.queue_error("could not parse Sorter configuration",
                                    f"Sorter hierarchy is required when resolve_equal_sort_method is '{resolve_method}'")
            elif not isinstance(hierarchy, list):
                MEM.queue_error("could not parse Sorter configuration",
                                f"Sorter hierarchy must be a list, not {type(hierarchy).__name__}")
            elif isinstance(hierarchy, list):

                with MEM.branch("validating Sorter hierarchy"):
                    fg_names = [fg.name for fg in self.filter_groups]

                    # handling filter hierarchy case
                    if self.resolve_equal_sort_method == "fiter_hierarchy":
                            fr = get_registry_copy()
                            for i, f in enumerate(hierarchy):
                                if isinstance(f, str):
                                    if f in fr.keys():
                                        fr.pop(f)
                                    else:
                                        MEM.queue_error("could not validate filter hierarchy",
                                                        f"Filter \"{f}\" does not exist")
                                else:
                                     MEM.queue_error("could not validate Filter hierarchy",
                                                    f"the hierarchy is not a list of strings but has an object of type \"{type(f).__name__}\" at index {i}")
                            if len(fr) > 0:
                                MEM.queue_error("could not validate filter hierarchy",
                                                f"not all filters were listed in the hierarchy.\nMissing Filters: {fr}")
                            self.hierarchy: list[str] = hierarchy

                    # handling group hierarchy case
                    elif self.resolve_equal_sort_method == "group_hierarchy":
                        for i, g in enumerate(hierarchy):
                            if isinstance(g, str):
                                if g in self.filter_groups:
                                    fg_names.remove(g)
                                else:
                                    MEM.queue_error("could not validate Group hierarchy",
                                                    f"\"{g}\" is not a Filter Group in the \"{self.name}\" sorter")
                                self.hierarchy: list[str] = hierarchy
                            else:
                                MEM.queue_error("could not validate Group hierarchy",
                                                f"the hierarchy is not a list of strings but has an object of type \"{type(g).__name__}\" at index {i}")
                    else:
                        logger.warning(f"'{self.name}' defines a hierarchy, even though 'resolve_equal_sort_method' is not 'group_hierarchy' or 'fiter_hierarchy'. Ignoring...")


    def verify_input_files(self):
        pillow_heif.register_heif_opener() # support heif
        with MEM.branch(f"validating the input files located in the input folder defined in the {self.name} Sorter"):
            files = [f for f in self.input_folder.iterdir() if f.is_file()]
            for file in files:
                try:
                    with Image.open(file) as img:
                        img.verify()
                    self.queue.append(file)
                except:
                    MEM.queue_error("could not verify all files in input folder",
                                    f"File '{file}' is not compatible")
        MEM.throw_if_errors()

    def sort(self):
        pillow_heif.register_heif_opener() # support heif

        for img in self.queue:
            conform_fgs:list[FilterGroup] = []
            
            for fg in self.filter_groups:
                if fg.filter_all(img):
                    conform_fgs.append(fg)

            if len(conform_fgs) > 1:
                conform_fgs = handle_conflict(handler_name = self.resolve_equal_sort_method,
                                              conform_fgs  = conform_fgs,
                                              hierarchy    = self.hierarchy)
            if len(conform_fgs) == 0:
                conform_fgs.append(FilterGroup(name="other", filters={}))

            actually_sort(method_name        = self.method,
                          filter_group_names = [cf.name for cf in conform_fgs],
                          image_path         = img,
                          output_folder      = self.output_folder)
                
                