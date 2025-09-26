class Coords:
    def __init__(self, coords: str, radius: int) -> None:
        self.coords = coords
        self.radius = radius

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass