import sys
import copy
import random
import math

import numpy

import basedata

mapsize = 100

# encapsulate TSP data: instance + starting solutions to optimise for
# benchmarking purpose
class TSPData(basedata.TSPData):
    def __init__(self, n, d):
        self.n, self.d = n, numpy.array(d)

