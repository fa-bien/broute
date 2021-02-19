import sys
import copy
import random
import math
import functools

mapsize = 100

# encapsulate TSP data: instance + starting solutions to optimise for
# benchmarking purpose
class TSPData:
    def __init__(self, n, d):
        self.n = n
        self.d = functools.reduce(lambda x, y: x+y, d)
        self.aux = [ float(x) for x in self.d ]
        self.aux2 = [ float(x) for x in self.d ]
