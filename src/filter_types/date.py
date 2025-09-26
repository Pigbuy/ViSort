class Date:
    def __init__(self, start_date: str, end_date: str, start_time: str, end_time: str) -> None:
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time

    def validate(self) -> bool:
        pass

    def filter(self, image) -> bool:
        pass