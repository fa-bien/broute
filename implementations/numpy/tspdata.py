import sys
import copy
import random
import math

import numpy

mapsize = 100

# encapsulate TSP data: instance + starting solutions to optimise for
# benchmarking purpose
class TSPData:
    def __init__(self, n, d):
        self.n, self.d = n, numpy.array(d)
        # auxiliary graph used e.g. for storing reduced costs (espprc)
        # or flow values (maxflow)
        # Typically it is used many times but only needs to be allocated once
        # and represents some kind of input data, therefore this is a good
        # place to have it.
        # dummy values to begin with...
        self.aux = numpy.array([ [ float(x) for x in row ] for row in d ])
        self.aux2 = numpy.array([ [ float(x) for x in row ] for row in d ])
