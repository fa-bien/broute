import os, sys
import numpy as np
from itertools import chain

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
        for p1 in range(len(tour) - 3):
            for p2 in range(p1+2, len(tour) - 1):
                if d[tour[p1]][tour[p1+1]] + d[tour[p2]][tour[p2+1]] > \
                   d[tour[p1]][tour[p2]] + d[tour[p1+1]][tour[p2+1]]:
                    # improving 2-exchange found
                    for i in range((p2-p1+1) // 2):
                        tour[p1+1+i], tour[p2-i] = tour[p2-i], tour[p1+1+i]
                    return True
        return False

    def or_opt(self):
        t = 0
        while self.firstorimprovement():
            t += 1
        return t
        
    def firstorimprovement(self):
        # actually speeds things up!
        tour, d = self.nodes, self.data.d
        for i in range(1, len(tour) - 1):
            for l in range(1, 1 + min(3, len(tour)-1-i)):
                for p in chain(range(i-1), range(i+l, len(tour)-1)):
                    delta = d[tour[i-1]][tour[i+l]] + d[tour[p]][tour[i]] + \
                        d[tour[i+l-1]][tour[p+1]] - d[tour[p]][tour[p+1]]\
                        - d[tour[i-1]][tour[i]] - d[tour[i+l-1]][tour[i+l]]
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
    
    def dumpstring(self):
        return str(self.nodes)
