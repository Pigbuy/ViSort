import logging
from pathlib import Path
from cli_args import args
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(str(Path(args.config_location).parent / "log.txt")),  # log to file
        #logging.StreamHandler()          # log to console
    ]
)
logger = logging.getLogger(__name__)