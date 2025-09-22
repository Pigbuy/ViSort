from enum import Enum

class ValidArgs(Enum):

    config_location = ("c", ".config.ini", "file")

    input_location = ("i", ".Input/", "folder")
    sorted_location = ("s", ".Sorted/", "folder")
    attributes_location = ("a", ".Attributes/", "folder")
    faces_location = ("f", ".Faces/", "folder")
    face_cache_location = ("fc", ".FaceCache/", "folder")
    
    single_run = ("sr", "", "binary")
    monitor_mode = ("m", "", "binary")
    no_face_caching = ("nfc", "", "binary")
    no_face_recognition = ("nfr", "", "binary")

    #noconf_mode = "noconf", ""
    #noconf_auto_word_count = "nawc", "5, "number""
    #noconf_sort_words = "nsw", ""

    def __init__(self, short: str, default: str, arg_type: str) -> None:
        self.short = short
        self.default = default
        self.arg_type = arg_type