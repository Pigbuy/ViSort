import argparse
import configparser
import os
from pathlib import Path
from PIL import Image

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

#import asyncio
#from concurrent.futures import ThreadPoolExecutor

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Image processing pipeline")

    # config
    parser.add_argument(
        "-c", "--config-location",
        default=".config.ini",
        help="Path to config file (default: .config.ini)"
    )

    # folders
    parser.add_argument("-i", "--input-location", default=".Input/", help="Input folder")
    parser.add_argument("-s", "--sorted-location", default=".Sorted/", help="Sorted folder")
    parser.add_argument("-a", "--attributes-location", default=".Attributes/", help="Attributes folder")
    parser.add_argument("-f", "--faces-location", default=".Faces/", help="Faces folder")
    parser.add_argument("--fc", "--face-cache-location", dest="face_cache_location",
                        default=".FaceCache/", help="Face cache folder")

    # flags
    parser.add_argument("--sr", "--single-run", dest="single_run",
                        action="store_true", help="Run once and exit")
    parser.add_argument("-m", "--monitor-mode", action="store_true", help="Enable monitor mode")
    parser.add_argument("--nfc", "--no-face-caching", dest="no_face_caching",
                        action="store_true", help="Disable face caching")
    parser.add_argument("--nfr", "--no-face-recognition", dest="no_face_recognition",
                        action="store_true", help="Disable face recognition")
    parser.add_argument("--nac", "--no-auto-convert", dest="no_auto_convert",
                        action="store_true", help="Do not auto-convert non-JPEGs")
    
    #noconf_mode = "noconf", ""
    #noconf_auto_word_count = "nawc", "5, "number""
    #noconf_sort_words = "nsw", ""

    return parser


def validate_image(img: Image.Image) -> bool:
    try:
        img.verify()
        return True
    except Exception:
        return False


def main():
    parser = build_parser()
    args = parser.parse_args()

    # config file
    config = configparser.ConfigParser()
    successfull_reads = config.read(args.config_location)
    if not successfull_reads:
        logger.critical("Failed to read config file")
        raise FileNotFoundError(f"Failed to read config file: {args.config_location}")
    logger.debug("read config")

    # prepare folders
    folders = [
        args.input_location,
        args.sorted_location,
        args.attributes_location,
        args.faces_location,
        args.face_cache_location,
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    logger.debug("all folders created or existed already")

    # collect images
    input_folder = Path(args.input_location)
    jpegs: list[Path] = []
    non_jpegs: list[Path] = []
    
    for f in input_folder.iterdir():
        if f.is_file():
            with Image.open(f) as oi:
                if validate_image(oi):
                    logger.debug(f"{f} is a valid image")
                    if oi.format == "JPEG":
                        jpegs.append(f)
                    else:
                        non_jpegs.append(f)
                else:
                    logger.warning(f"{f} is not a valid image")

    logger.info(f"found {len(jpegs)} jpeg images")
    non_jpeg_amount = len(non_jpegs)
    logger.info(f"found {non_jpeg_amount} non-jpeg images")

    image_queue = jpegs.copy()
    logger.debug("added jpegs to queue")

    if not args.no_auto_convert:
        logger.info(f"converting {non_jpeg_amount} non jpeg images to jpeg")
        for index, ip in enumerate(non_jpegs):
            with Image.open(ip) as oi:
                ci = oi.convert("RGB")
                new_path = ip.with_suffix(".jpg")
                ci.save(new_path, "JPEG")
                ip.unlink(missing_ok=True)
                image_queue.append(new_path)
                logger.info(f"converted {index+1}/{non_jpeg_amount} non-jpegs to jpeg")


    


if __name__ == "__main__":
    main()