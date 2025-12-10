import argparse
import os
from pathlib import Path

from tqdm import tqdm
from PIL import Image
import threading
from queue import Queue
from typing import List, cast
import time

from configuration import Configuration
from logger import logger
from Errors import MEM

import pillow_heif
from sorting.sorter import Sorter
pillow_heif.register_heif_opener()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Image processing pipeline")

    # config
    parser.add_argument(
        "-c", "--config-location",
        default="config.toml",
        help="Path to config file (default: config.toml)"
    )

    # folders
#    parser.add_argument("-i", "--input-location", default=".Input/", help="Input folder")
#    parser.add_argument("-s", "--sorted-location", default=".Sorted/", help="Sorted folder")
#    parser.add_argument("-a", "--attributes-location", default=".Attributes/", help="Attributes folder")
#    parser.add_argument("-f", "--faces-location", default=".Faces/", help="Faces folder")
#    parser.add_argument("--fc", "--face-cache-location", dest="face_cache_location",
#                        default=".FaceCache/", help="Face cache folder")

    # flags
#    parser.add_argument("--sr", "--single-run", dest="single_run",
#                        action="store_true", help="Run once and exit")
#    parser.add_argument("-m", "--monitor-mode", action="store_true", help="Enable monitor mode")
#    parser.add_argument("--nfc", "--no-face-caching", dest="no_face_caching",
#                        action="store_true", help="Disable face caching")
#    parser.add_argument("--nfr", "--no-face-recognition", dest="no_face_recognition",
#                        action="store_true", help="Disable face recognition")
#    parser.add_argument("--nac", "--no-auto-convert", dest="no_auto_convert",
#                        action="store_true", help="Do not auto-convert non-JPEGs")
    
    #noconf_mode = "noconf", ""
    #noconf_auto_word_count = "nawc", "5, "number""
    #noconf_sort_words = "nsw", ""

    return parser

def sort_sorters_by_priority(config:Configuration) -> dict[int, list[Sorter]]:
    priority_sorter_list:dict[int,list[Sorter]] = {}
    def add(key: int, value):
        if key not in priority_sorter_list:
            priority_sorter_list[key] = []
        priority_sorter_list[key].append(value)

    for s in config.sorters:
        add(s.priority,s)
    
    return dict(sorted(priority_sorter_list.items()))

        

def main():
    args = build_parser().parse_args()
    try:
        cp = Path(args.config_location)
        if not cp.exists():
            MEM.queue_error("could not read configuration file",
                            f"configuration file \"{cp}\" does not exist")
    except:
        MEM.queue_error("could not read configuration file",
                        f"could not make a path object from the specified path or couldn't verify it's existence")
    MEM.throw_if_errors()

    config:Configuration = Configuration(Path(args.config_location)) # parse the configuration file and throw errors if anything is wrong

    psl:dict[int, list[Sorter]] = sort_sorters_by_priority(config=config)

    for priority, sorters in tqdm(psl.items(),
                                  desc=f"sorter priorities",
                                  total=len(psl),
                                  position=0, unit="priorities"):

        for sorter in cast(list[Sorter],
                           tqdm(sorters,
                                desc=f"sorters of priority {priority}",
                                total=len(sorters),
                                position=1,
                                unit="sorters")):
            sorter.sort()







if __name__ == "__main__":
    main()