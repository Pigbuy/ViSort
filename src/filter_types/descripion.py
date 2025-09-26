class Description:
    def __init__(self, desc: str) -> None:
        self.desc = desc

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass