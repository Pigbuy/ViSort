import argparse

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

args = build_parser().parse_args()