import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        #logging.FileHandler("app.log"),  # log to file
        logging.StreamHandler()          # log to console
    ]
)
logger = logging.getLogger(__name__)