from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from datetime import datetime
from dateutil import parser
from logger import logger
from typing import Optional


class Date(FilterArgType):
    @staticmethod
    def validate_str(string: str) -> bool:
        """
        Validates if the input string can be parsed as a date.
        Accepts various date formats like:
        - YYYY-MM-DD
        - DD/MM/YYYY
        - Month DD, YYYY
        - Natural language dates (e.g., 'today', 'yesterday', 'last week')
        """
        try:
            parser.parse(string)
            return True
        except (ValueError, TypeError):
            logger.critical(f"Invalid date format: {string}")
            return False

    def parse_valid_string(self, valid_string: str) -> "Date":
        """
        Parses a validated date string into a datetime object
        """
        self.date = parser.parse(valid_string)
        return self

    def __init__(self, date: Optional[datetime] = None) -> None:
        """
        Initialize with an optional datetime object
        """
        self.date = date

    def __str__(self) -> str:
        """
        Returns a string representation of the date in ISO format
        """
        return self.date.isoformat() if self.date else ""

    def get_days_difference(self, other_date: datetime) -> float:
        """
        Returns the number of days between this date and another date.
        Returns infinity if either date is None.
        """
        if not self.date or not other_date:
            return float('inf')
        return abs((self.date - other_date).days)

    def is_before(self, other_date: datetime) -> bool:
        """
        Returns True if this date is before the other date
        """
        return bool(self.date and other_date and self.date < other_date)

    def is_after(self, other_date: datetime) -> bool:
        """
        Returns True if this date is after the other date
        """
        return bool(self.date and other_date and self.date > other_date)

    def is_same_day(self, other_date: datetime) -> bool:
        """
        Returns True if both dates are on the same day
        """
        return bool(self.date and other_date and self.date.date() == other_date.date())
