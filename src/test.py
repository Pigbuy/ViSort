from filter_types.filter_arg_types.interval import Interval
from Errors import MEM

with MEM.branch("making interval"):
    i = Interval(input())
print(i.contains(float(input())))
MEM.throw_if_errors()