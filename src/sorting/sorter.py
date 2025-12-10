from pathlib import Path
from logger import logger
from Errors import MEM
from filter_group import FilterGroup
import shutil
import os
from PIL import Image
from PIL.Image import Exif
import pillow_heif
import json


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
            valid_methods = {"move", "link", "tag", "name", "json", "none"}
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
        def move(filter_group_names:list[str], image_path: Path, output_folder:Path):
            """makes (a) subfolder(s) in the output_folder named according to the filter_group_names(or just check if they exist and are writable if it already exists), moves copies of the original image in those folders and then deletes the original image folder"""
            for f in filter_group_names:
                fg_folder = output_folder / f
                fg_folder.mkdir(parents=True, exist_ok=True)
                shutil.copy2(image_path,fg_folder)
            os.remove(image_path)
        
        @staticmethod
        def link(filter_group_names:list[str], image_path: Path, output_folder:Path):
            """makes (a) subfolder(s) in the output_folder named according to the filter_group_names(or just check if they exist and are writable if it already exists) and places a symlink of the original image in those folders."""
            for f in filter_group_names:
                fg_folder = output_folder / f
                fg_folder.mkdir(parents=True, exist_ok=True)
                os.symlink(image_path.resolve(), fg_folder / image_path.name)
        
        @staticmethod
        def tag(filter_group_names:list[str], image_path: Path):
            """appends filter_group_names seperated with commas to the exif metadata description"""
            img = Image.open(image_path)
            exif_data = img.getexif()
            tags_str = ", ".join(filter_group_names)
            exif_data[270] = tags_str  # 270 is ImageDescription tag
            img.save(image_path, exif=exif_data)
        
        @staticmethod
        def name(filter_group_names:list[str], image_path: Path):
            """changes the image file name to: `{filter_group_names(seperated with underscores)}{index of picture with the same filter_group_names combination}`"""
            new_name = "_".join(filter_group_names) + image_path.suffix
            new_path = image_path.parent / new_name
            image_path.rename(new_path)
        
        @staticmethod
        def json(filter_group_names:list[str], image_path: Path, output_folder:Path):
            """Create/update ViSort.json(located in the output_folder) with the image added to the given filter groups."""
            json_path = output_folder / "ViSort.json"
            image_str = str(image_path)

            if json_path.exists():
                with open(json_path) as f:
                    data = json.load(f)
            else:
                data = {}

            for fgn in filter_group_names:
                data.setdefault(fgn, [])
                data[fgn].append(image_str)
            
            with open(json_path, "w") as f:
                json.dump(data, f, indent=2)

        @staticmethod
        def none():
            """doesn't sort anything"""
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
        pillow_heif.register_heif_opener() # support heif
        pass