import sys
import copy
from itertools import chain

import tspdata
import espprc
import espprcindex
import maxflow

class TSPSolution:
    def __init__(self, data, permutation):
        self.data = data
        self.nodes = copy.copy(permutation)

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
                        t = [ x for x in tour[i:i+l] ]
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
                del tmp[where]
                where += 1
            # step 2: repair
            while len(unplanned) > 0:
                bestcost, bestnode, bestfro, bestto = sys.maxsize, -1, -1, -1
                for (fro, k) in enumerate(unplanned):
                    for ((pos, i), j) in zip(enumerate(tmp[:-1]), tmp[1:]):
                        delta = d(i, k) + d(k, j) - d(i, j)
                        if delta < bestcost:
                            bestcost = delta
                            bestnode, bestfro, bestto = k, fro, pos
                # perform best found insertion
                tmp.insert(bestto+1, bestnode)
                del unplanned[bestfro]
                checksum += bestcost
                # step 3: move or not (in our case always move)
            self.nodes = tmp
        return checksum

    # Max. length constraint: current tour length is max. length
    # Each node consumes one resource per 1-bit of its binary representation,
    # the first bit being bit 0
    # For instance 6 consumes 1 unit of resource 1 and 1 unit of resource 2,
    # since 6 = 2^1 + 2^2
    def espprc(self, nresources=6, resourcecapacity=1, index=False):
        n, tour, d = self.data.n, self.nodes, self.data.d
        # update reduced costs
        dual = [ 0.0 for x in range(n) ]
        for (i, j) in zip(tour[:-1], tour[1:]):
            dual[j] = d(i, j)
        for i in range(n):
            for j in range(n):
                self.data.setaux(i, j, float(d(i, j) - dual[j]))
        # max len: sum of best assignments
        maxlen = sum([ min([d(i, j) for j in range(n) if i != j])
                       for i in range(n)])
        if not index:
            e = espprc.ESPPRC(n, d, self.data.aux,
                              self.nodes, nresources, resourcecapacity, maxlen)
        else:
            e = espprcindex.ESPPRCLC(n, d, self.data.aux,
                                     self.nodes, nresources, resourcecapacity,
                                     maxlen)
        return int(e.solve())

    # max. flow
    # arc capacity = arc cost divided by ten but only for those arcs that are
    # above the average value of arcs with the same destination
    def maxflow(self, algorithm='EK'):
        n, tour, d = self.data.n, self.nodes, self.data.d
        cap, flow = self.data.aux, self.data.aux2
        setcap, setflow = self.data.setaux, self.data.setaux2
        # first we build the capacity graph
        t = [ 0.0 for x in range(n) ]
        for (i, j) in zip(tour[:-1], tour[1:]):
            t[j] = d(i, j)
        for j in range(n):
            for i in range(n):
                setcap(i, j, d(i, j) / 1000 if d(i, j)>t[j] else 0.0)
        # then we solve it for each non-0 node as sink
        checksum = 0.0
        for sink in range(1, n):
            mf = maxflow.edmondskarp(cap, flow, setflow, n, 0, sink)
            checksum += mf
        return int(checksum)
    
    def cost(self):
        total = 0
        for i, j in zip(self.nodes[:-1], self.nodes[1:]):
            total += self.data.d(i, j)
        return total
