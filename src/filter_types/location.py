# arg type imports
from filter_arg_types.location import Location

# Filter Type imports
from filter_types.filter_type import FilterType
from filter_types.filter_types import register

# src modules imports
from Errors import MEM
from logger import logger

# builtin imports
from pathlib import Path
from typing import Optional, Union

# library imports
from PIL import Image
import pillow_heif

@register("location")
class Loc(FilterType):
    def __init__(self) -> None:
        super().__init__()
    
    def filter(self, image: Path) -> bool:
        pillow_heif.register_heif_opener() # support heif
        pass