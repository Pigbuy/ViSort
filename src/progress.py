from asyncio import Queue
from logger import logger

from typing import cast

from tqdm import tqdm


event_queue:Queue[dict] = Queue()

async def progress_and_debug_loop(config):
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