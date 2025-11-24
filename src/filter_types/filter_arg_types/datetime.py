from filter_types.filter_arg_types.filter_arg_type import FilterArgType
from filter_types.filter_arg_types.filter_arg_types import register
from datetime import datetime
from dateutil import parser
from Errors import MEM


@register("datetime")
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
            MEM.queue_error("Couldn't validate DateTime",
                            "wrong formatting")
            return False
        
    @staticmethod
    def from_valid_str(valid_string: str) -> "DateTime":
        return DateTime(parser.parse(valid_string))

    def __init__(self, dt: datetime) -> None:
        self.datetime = dt

    @property
    def dt(self) -> datetime:
        """Compatibility property expected by filters: returns underlying datetime."""
        return self.datetime

    def is_before(self, other_dt: datetime) -> bool:
        return bool(self.datetime and other_dt and self.datetime < other_dt)

    def is_after(self, other_dt: datetime) -> bool:
        return bool(self.datetime and other_dt and self.datetime > other_dt)