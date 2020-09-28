import itertools as it
import numpy as np
from numba import jit

from tspdata import dist

class TSPSolution:
    def __init__(self, data, permutation):
        self.data = data
        self.nodes = np.array(permutation)

    def two_opt(self):
        t = 0
        while self.first2eimprovement():
            t += 1
        return t

    def first2eimprovement(self):
        # actually speeds things up!
        tour, d, n = self.nodes, self.data.d, self.data.n
        return aux_2opt(tour, d, n)

    def or_opt(self):
        t = 0
        while self.firstorimprovement():
            t += 1
        return t
        
    def firstorimprovement(self):
        # actually speeds things up!
        tour, d, n = self.nodes, self.data.d, self.data.n
        return aux_oropt(tour, d, n)
    
@jit(nopython=True)
def aux_2opt(tour, d, n):
    for p1 in range(len(tour) - 3):
        for p2 in range(p1+2, len(tour) - 1):
            if dist(d, n, tour[p1], tour[p1+1]) + dist(d, n, tour[p2], tour[p2+1]) > \
               dist(d, n, tour[p1], tour[p2]) + dist(d, n, tour[p1+1], tour[p2+1]):
                # improving 2-exchange found
                for i in range((p2-p1+1) // 2):
                    tour[p1+1+i], tour[p2-i] = tour[p2-i], tour[p1+1+i]
                return True
    return False

@jit(nopython=True)
def aux_oropt(tour, d, n):
    for i in range(1, len(tour) - 1):
        for l in range(1, 1 + min(3, len(tour)-1-i)):
            for tmp in (range(i-1), range(i+l, len(tour)-1)):
                for p in tmp:
                    delta = dist(d, n, tour[i-1], tour[i+l]) + dist(d, n, tour[p], tour[i]) + \
                        dist(d, n, tour[i+l-1], tour[p+1]) - dist(d, n, tour[p], tour[p+1])\
                        - dist(d, n, tour[i-1], tour[i]) - dist(d, n, tour[i+l-1], tour[i+l])
                    # perform improving move
                    if delta < 0:
                        # store sequence to move
                        t = np.array([ x for x in tour[i:i+l] ])
                        if i < p:
                            # shift stuff left
                            tour[i:p-l+1] = tour[i+l:p+1]
                            # copy sequence right of the stuff
                            tour[p+1-l:p+1] = t[:]
                        else:
                            # shift stuff right
                            tour[i-1+l:p+l:-1] = tour[i-1:p:-1]
                            # copy sequence right of the stuff
                            tour[p+1:p+1+l] = t[:]
                        return True
    return False
