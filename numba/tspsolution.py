import itertools as it
import numpy as np
from numba import jit

import tspdata

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
        tour, d = self.nodes, self.data.d
        return aux_2opt(tour, d)

    def or_opt(self):
        t = 0
        while self.firstorimprovement():
            t += 1
        return t
        
    def firstorimprovement(self):
        # actually speeds things up!
        tour, d = self.nodes, self.data.d
        return aux_oropt(tour, d)
    
@jit(nopython=True)
def aux_2opt(tour, d):
    for p1 in range(len(tour) - 3):
        for p2 in range(p1+2, len(tour) - 1):
            if d[tour[p1]][tour[p1+1]] + d[tour[p2]][tour[p2+1]] > \
               d[tour[p1]][tour[p2]] + d[tour[p1+1]][tour[p2+1]]:
                # improving 2-exchange found
                for i in range((p2-p1+1) // 2):
                    tour[p1+1+i], tour[p2-i] = tour[p2-i], tour[p1+1+i]
                return True
    return False

@jit(nopython=True)
def aux_oropt(tour, d):
    for i in range(1, len(tour) - 1):
        for l in range(1, 1 + min(3, len(tour)-1-i)):
            for tmp in (range(i-1), range(i+l, len(tour)-1)):
                for pos in tmp:
                    delta = d[tour[i-1]][tour[i+l]] + d[tour[pos]][tour[i]] + \
                        d[tour[i+l-1]][tour[pos+1]] - d[tour[pos]][tour[pos+1]]\
                        - d[tour[i-1]][tour[i]] - d[tour[i+l-1]][tour[i+l]]
                    # perform improving move
                    if delta < 0:
                        if i < pos:
                            nt = np.hstack((tour[:i],
                                            tour[i+l:pos+1],
                                            tour[i:i+l],
                                            tour[pos+1:]))
                        else:
                            nt = np.hstack((tour[0:pos+1],
                                            tour[i:i+l],
                                            tour[pos+1:i],
                                            tour[i+l:]))
                        #
                        tour[:] = nt
                        return True
    return False
