import asyncio
import os
from pathlib import Path

from tqdm import tqdm
from PIL import Image
import threading
from asyncio import Queue
from typing import List, cast
import time

from configuration import Configuration
from logger import logger
from Errors import MEM
from cli_args import args
from progress import progress_and_debug_loop

import pillow_heif
from sorting.sorter import Sorter
pillow_heif.register_heif_opener()

event_queue:Queue[dict] = Queue()

async def main():
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
    logger.info(f"parsed config file{args.config_location}")

    for sorter in config.sorters:
        asyncio.create_task(sorter.watch_input_folder())
    logger.info("started sorting")

    await progress_and_debug_loop(config)

if __name__ == "__main__":
    asyncio.run(main())