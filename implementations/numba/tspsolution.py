import sys
import itertools as it
import numpy as np
from numba import jit

import tspdata
import maxflow

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

    def lns(self, niter=10):
        sys.stderr.write('Not valid: numba implementation of lns\n')
        sys.stderr.write('\tdeleting from array is not implemented in numba\n')
        sys.exit(95)
        return float('Inf')
        tour, d = self.nodes, self.data.d
        return aux_lns(tour, d, niter)
    
    def maxflow(self):
        return aux_maxflow(self.data.n, self.data.d, self.data.aux,
                           self.data.aux2, self.nodes)
    
@jit(nopython=True)
def aux_2opt(tour, d):
    for p1 in range(len(tour) - 3):
        for p2 in range(p1+2, len(tour) - 1):
            if d[tour[p1],tour[p1+1]] + d[tour[p2],tour[p2+1]] > \
               d[tour[p1],tour[p2]] + d[tour[p1+1],tour[p2+1]]:
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
                for p in tmp:
                    delta = d[tour[i-1],tour[i+l]] + d[tour[p],tour[i]] + \
                        d[tour[i+l-1],tour[p+1]] - d[tour[p],tour[p+1]]\
                        - d[tour[i-1],tour[i]] - d[tour[i+l-1],tour[i+l]]
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

# currently not working: np.insert not supported by numba...
@jit(nopython=True)
def aux_lns(tour, d, niter):
    checksum = 0
    for iter in range(niter):
        # step 0: copy solution
        tmp = tour.copy()
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
                    delta = d[i,k] + d[k,j] - d[i,j]
                    if delta < bestcost:
                        bestcost, bestfro, bestto = delta, fro, pos
            # perform best found insertion
            tmp = np.insert(tmp, bestto+1, bestnode)
            del unplanned[bestfro]
            checksum += bestcost
            # step 3: move or not (in our case always move)
        tour = tmp
    return checksum
    
# max. flow
# arc capacity = arc cost divided by ten but only for those arcs that are
# above the average value of arcs with the same destination
@jit(nopython=True)
def aux_maxflow(n, d, cap, flow, tour):
    # first we build the capacity graph
    t = np.array([ 0.0 for x in range(n) ])
    for (i, j) in zip(tour[:-1], tour[1:]):
        t[j] = d[i,j]
    for j in range(n):
        for i in range(n):
            cap[i,j] = d[i,j] / 1000 if d[i,j] > t[j] else 0.0
    # then we solve it for each non-0 node as sink
    checksum = 0.0
    for sink in range(1, n):
        mf = maxflow.edmondskarp(cap, flow, n, 0, sink)
        checksum += mf
    # print(checksum, '\t', int(checksum))
    return int(checksum)
