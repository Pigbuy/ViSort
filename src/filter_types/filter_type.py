from pathlib import Path

class FilterType():
    """"A Filter Type is is a type of Filter. This Filter has Filter arg types as its attributes and can factor them in, in order to filter an image"""
    def __init__(self, args:dict) -> None:
        self.TYPE:str = "base_class"
        pass

    async def filter(self, image:Path, sorter) -> bool:
        """checks if the image complies with the filter"""
        return True