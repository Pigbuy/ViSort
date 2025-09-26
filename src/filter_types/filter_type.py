from enum import Enum

class FilterType():
    class Args(Enum):
        def __init__(self, required:bool, type:) -> None:
            self.required = required
            self.type = type
            super().__init__()

    def __init__(self) -> None:
        pass
    
    def validate(self) -> bool: return True
    def filter(self, image) -> bool: return True