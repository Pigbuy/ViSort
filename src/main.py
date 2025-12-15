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
    logger.info("parsed config file")

    for sorter in config.sorters:
        asyncio.create_task(sorter.watch_input_folder(event_queue=event_queue))
    logger.info("started sorting")

    bars:dict[str,tqdm] = {}
    status_bars:dict[str,tqdm] = {}

    for i,sorter in enumerate(config.sorters):
        bars[sorter.name] = tqdm(position = 2 * i,total=0,desc=f"{sorter.name} Sorter progress", unit="img")
        status_bars[sorter.name] = tqdm(position = 2 * i + 1,bar_format='↳ {desc}')

    while True:
        
        e = await event_queue.get()  # let tasks do their thing until a task sends an event
        
        type = e.get("type")
        match type:
            case None:
                pass
            case "finished sorting image":
                bar = bars[e["sorter"]]
                status_bar = status_bars[e["sorter"]]
                if bar.n >= cast(int,bar.total):
                    bar.n = 0
                    bar.total = 0
                else:
                    bar.update(n=1)
                    status_bar.desc = f"sorted '{e["image"]}' into '{", ".join(cast(list,e["dest"]))}' using method '{e["method"]}'"
                    logger.info(f"{e["sorter"]}: {status_bar.desc}")
                status_bar.refresh()
                bar.refresh()

            case "found new images to sort":
                bar = bars[e["sorter"]]
                status_bar = status_bars[e["sorter"]]
                bar.total  += e["amount"]
                status_bar.desc = f"found {e["amount"]} new images to sort"
                logger.info(f"{e["sorter"]}: {status_bar.desc}")
                status_bar.refresh()
                bar.refresh()
            
            case "message":
                status_bar = status_bars[e["sorter"]]
                status_bar.desc = str(e["message"])
                logger.info(f"{e["sorter"]}: {status_bar.desc}")
                status_bar.refresh()



if __name__ == "__main__":
    asyncio.run(main())