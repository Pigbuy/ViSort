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
        self.datetime = parser.parse(valid_string)
        return self

    def __init__(self, dt: Optional[datetime] = None) -> None:
        self.datetime = dt

    def is_before(self, other_dt: datetime) -> bool:
        return bool(self.datetime and other_dt and self.datetime < other_dt)

    def is_after(self, other_dt: datetime) -> bool:
        return bool(self.datetime and other_dt and self.datetime > other_dt)