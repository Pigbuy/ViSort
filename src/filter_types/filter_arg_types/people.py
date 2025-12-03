from main import args
from pathlib import Path
from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from Errors import MEM


class People(FilterArgType):
    def __init__(self, string:str):
        valid = True
        people_path:Path =  Path(args.faces_location)
        valid_people: list[str] = []
        for f in people_path.iterdir():
            name = f.name
            if f.is_file() and "." in name:
                name = name.split(".")[0]
            valid_people.append(name)
        
        people_to_check = string.split(",")
        for person in people_to_check:
            if person not in valid_people:
                MEM.queue_error(f"Couldn't find {person} in people folder",
                                    f"there is no image or folder named {person} in the people folder")
                valid = False

        if valid:
            self.people = tuple(string.split(","))
        else:
            self.people = ()