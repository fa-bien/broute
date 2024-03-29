import sys
import copy
from itertools import chain
import numpy as np

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
                if d(tour[p1], tour[p1+1]) + d(tour[p2], tour[p2+1]) > \
                   d(tour[p1], tour[p2]) + d(tour[p1+1], tour[p2+1]):
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
                    delta = d(tour[i-1], tour[i+l]) + d(tour[p], tour[i])\
                        + d(tour[i+l-1], tour[p+1]) - d(tour[p], tour[p+1])\
                        - d(tour[i-1], tour[i]) - d(tour[i+l-1], tour[i+l])
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

    def lns(self, niter=10):
        d = self.data.d
        checksum = 0
        for iter in range(niter):
            # step 0: copy solution
            tmp = copy.copy(self.nodes)
            unplanned = []
            # step 1: destroy
            where = 1
            while where < len(tmp) - 1:
                unplanned.append(tmp[where])
                tmp = np.delete(tmp, where)
                where += 1
            # step 2: repair
            while len(unplanned) > 0:
                bestcost, bestnode, bestfro, bestto = sys.maxsize, -1, -1, -1
                for (fro, k) in enumerate(unplanned):
                    for ((pos, i), j) in zip(enumerate(tmp[:-1]), tmp[1:]):
                        delta = d(i, k) + d(k, j) - d(i, j)
                        if delta < bestcost:
                            bestcost, bestfro, bestto = delta, fro, pos
                # perform best found insertion
                tmp = np.insert(tmp, bestto+1, bestnode)
                del unplanned[bestfro]
                checksum += bestcost
                # step 3: move or not (in our case always move)
            self.nodes = tmp
        return checksum
    
