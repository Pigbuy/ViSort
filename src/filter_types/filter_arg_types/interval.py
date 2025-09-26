from filter_types.filter_arg_types.filter_arg_type import FilterArgType
import re
import portion as P

class Interval(FilterArgType):
    @staticmethod
    def validate_str(string:str) -> bool:
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
            return False

        # ensure a < b with "a-b"
        if "-" in string and not string.startswith(("<", ">", "<=", ">=")):
            try:
                a, b = string.split("-")
                if float(a) >= float(b):
                    return False
            except ValueError:
                return False

        return True

    def parse_valid_string(self, valid_string:str) -> None:

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
            
        self.portion_interval = parse_interval(valid_string)

    def contains(self, number:float) -> bool:
        return number in self.portion_interval
    
    def __init__(self, portion_interval:P.Interval) -> None:
        self.portion_interval = portion_interval