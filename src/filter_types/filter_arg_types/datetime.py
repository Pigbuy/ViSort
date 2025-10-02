from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from datetime import datetime
from dateutil import parser
from logger import logger
from typing import Optional


class DateTime(FilterArgType):
    @staticmethod
    def validate_str(string: str) -> bool:
        """
        Validates if the input string can be parsed as a datetime.
        Accepts various formats like:
        - YYYY-MM-DD HH:MM:SS
        - DD/MM/YYYY HH:MM
        - Month DD, YYYY HH:MM AM/PM
        - Natural language (e.g., 'today at 2pm', 'yesterday noon')
        - Time only ('14:30', '2:30 PM') - uses current date
        - Date only ('2025-10-02') - uses midnight as time
        """
        try:
            parser.parse(string)
            return True
        except (ValueError, TypeError):
            logger.critical(f"Invalid date format: {string}")
            return False

    def parse_valid_string(self, valid_string: str) -> "DateTime":
        """
        Parses a validated datetime string into a datetime object
        """
        self.datetime = parser.parse(valid_string)
        return self

    def __init__(self, dt: Optional[datetime] = None) -> None:
        """
        Initialize with an optional datetime object
        """
        self.datetime = dt

    def __str__(self) -> str:
        """
        Returns a string representation of the datetime in ISO format
        """
        return self.datetime.isoformat() if self.datetime else ""

    def get_time_difference_minutes(self, other_dt: datetime) -> float:
        """
        Returns the total number of minutes between this datetime and another datetime.
        Returns infinity if either datetime is None.
        """
        if not self.datetime or not other_dt:
            return float('inf')
        diff = abs(self.datetime - other_dt)
        return diff.total_seconds() / 60

    def get_time_difference_days(self, other_dt: datetime) -> float:
        """
        Returns the number of days between this datetime and another datetime.
        Returns infinity if either datetime is None.
        """
        if not self.datetime or not other_dt:
            return float('inf')
        diff = abs(self.datetime - other_dt)
        return diff.total_seconds() / (24 * 3600)

    def is_before(self, other_dt: datetime) -> bool:
        """
        Returns True if this datetime is before the other datetime
        """
        return bool(self.datetime and other_dt and self.datetime < other_dt)

    def is_after(self, other_dt: datetime) -> bool:
        """
        Returns True if this datetime is after the other datetime
        """
        return bool(self.datetime and other_dt and self.datetime > other_dt)

    def is_same_day(self, other_dt: datetime) -> bool:
        """
        Returns True if both datetimes are on the same day
        """
        return bool(
            self.datetime and other_dt and 
            self.datetime.date() == other_dt.date()
        )

    def is_same_hour(self, other_dt: datetime) -> bool:
        """
        Returns True if both datetimes are in the same hour of the same day
        """
        return bool(
            self.datetime and other_dt and 
            self.datetime.date() == other_dt.date() and
            self.datetime.hour == other_dt.hour
        )

    def get_time(self) -> str:
        """
        Returns just the time portion in 24-hour format
        """
        return self.datetime.strftime("%H:%M:%S") if self.datetime else ""

    def get_date(self) -> str:
        """
        Returns just the date portion in ISO format
        """
        return self.datetime.date().isoformat() if self.datetime else ""
