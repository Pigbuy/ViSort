from filter_types.filter_arg_types.filter_arg_type import FilterArgType
import re
import portion as P
from Errors import MEM

class Interval(FilterArgType):

    def __init__(self, string:str):
        valid = True
        string = string.replace(" ","").replace("\t", "").replace("\n", "")
        pattern = re.compile(
            r"""^(
                (>=-?\d+(\.\d+)?) |      # >=number
                (<=-?\d+(\.\d+)?) |      # <=number
                (>-?\d+(\.\d+)?)  |      # >number
                (<-?\d+(\.\d+)?)  |      # <number
                (-?\d+(\.\d+)?-?-?\d+(\.\d+)?) |  # a-b
                (-?\d+(\.\d+)?)          # just number
            )$""",
            re.VERBOSE,
        )

        match = pattern.match(string)
        if not match:
            MEM.queue_error("Could not validate Interval",
                            "Interval format is invalid")
            valid = False

        # ensure a < b with "a-b"
        if "-" in string and not string.startswith(("<", ">", "<=", ">=")) and valid:
            try:
                a, b = string.split("-")
                if float(a) >= float(b):
                    MEM.queue_error("Could not validate Interval",
                                    "when handling explicit ranges, the first number must be smaller than the second, it isn't")
                    valid = False
            except ValueError:
                MEM.queue_error("Could not validate Interval",
                                "idk how this happened, but your interval format is just wrong")
                valid = False

        def parse_interval(expr: str) -> P.Interval:
            expr = expr.strip()

            if expr.startswith(">="):
                num = float(expr[2:])
                return P.closed(num, float("inf"))

            elif expr.startswith("<="):
                num = float(expr[2:])
                return P.closed(float("-inf"), num)

            elif expr.startswith(">"):
                num = float(expr[1:])
                return P.open(num, float("inf"))

            elif expr.startswith("<"):
                num = float(expr[1:])
                return P.open(float("-inf"), num)

            elif "-" in expr:
                left, right = map(float, expr.split("-", 1))
                if left >= right:
                    raise ValueError(f"Invalid interval: left {left} >= right {right}")
                return P.closed(left, right)

            else:
                num = float(expr)
                return P.singleton(num)

        if valid:
            self.portion_interval = parse_interval(string)
        else:
            self.portion_interval = P.open(float("-inf"), float("inf")) # default value it falls back to because why not
        
    def contains(self, number:float) -> bool:
        return number in self.portion_interval