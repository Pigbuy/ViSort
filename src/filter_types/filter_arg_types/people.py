from main import args
from pathlib import Path
from filter_types.filter_arg_types.filter_arg_type import FilterArgType


class People(FilterArgType):
    @staticmethod
    def validate_str(string:str) -> bool:
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
                return False
        return True
    
    def parse_valid_string(self, valid_string) -> "FilterArgType":
        self.people = valid_string.split(",")
        return self
    
    def __init__(self, people:tuple[str]) -> None:
        self.people = people