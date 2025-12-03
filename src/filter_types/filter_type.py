class FilterType():
    """"A Filter Type is is a type of Filter. This Filter has Filter arg types as its attributes and can factor them in, in order to filter an image"""
    def __init__(self) -> None:
        pass
    
    def filter(self, image) -> bool:
        """checks if the image complies with the filter"""
        return True