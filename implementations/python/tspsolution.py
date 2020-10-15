import sys
import copy
from itertools import chain
import collections

import tspdata

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
                        delta = d[i][k] + d[k][j] - d[i][j]
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
    def espprc(self, nresources=6, resourcecapacity=3):
        tour, d, rc = self.nodes, self.data.d, self.data.reducedcost
        vertices = range(self.data.n)
        maxlen = sum(d[i][j] for (i, j) in zip(tour[:-1], tour[1:]))
        # step 1: update reduced costs
        for (i, j) in zip(tour[:-2], tour[1:-1]):
            for k in range(self.data.n):
                rc[k][j] = float(d[k][j] - d[i][j])
        # step 2: initialise other DP data: list of labels, queue,
        #                                   initial label, resources
        Q, Qset = collections.deque(), set([0])
        Q.append(0)
        labels = [ [] for x in self.nodes ]
        Label.resources = [ x for x in range(nresources) ]
        labels[0].append(Label())
        # step 3: run DP
        while len(Qset) > 0:
            n = Q.pop()
            Qset.remove(n)
            for label in labels[n]:
                if not label.toextend: continue
                for succ in vertices:
                    if succ in label.visited or succ == n: continue
                    # succ is a candidate for extension; is it length-feasible?
                    if label.length + d[n][succ] + d[succ][0] > maxlen: continue
                    # is it resource-feasible?
                    rfeas = True
                    for i, r in enumerate(label.q):
                        if (succ & (1 << i) > 0) and r + 1 > resourcecapacity:
                            rfeas = False
                            break
                    if not rfeas: continue

                    print('Extending ', label, ' to ', succ)
                    
                    # now we can actually extend the label!
                    nl = label.extend(succ, rc, d)

                    print('\tnew label: ', nl)
                    
                    # Let's update dominance
                    added = updatedominance(labels[succ], nl)
                    if added and not (succ in Qset) and succ != 0:
                        Qset.add(succ)
                        Q.append(succ)
                label.toextend = False
        # step 4: return distance of cheapest label as hash value.
        print('Labels at node 0:')
        for l in labels[0]:
            print(l)
            sys.exit(9)
        return sum(sum(x) for x in rc)

    def cost(self):
        total = 0
        for i, j in zip(self.nodes[:-1], self.nodes[1:]):
            total += self.data.d[i][j]
        return total

# * compare newlabel with collection of labels removing dominated labels as
#   necessary
# * adds newlabels to collection labels if it is not dominated
# * returns true if newlabel was added
def updatedominance(labels, newlabel):
    i = 0
    while i < len(labels):
        if labels[i].dominates(newlabel):
            return False
        elif newlabel.dominates(labels[i]):
            if i < len(labels) - 1:
                labels[i] = labels[-1]
            del labels[i]
        else:
            i += 1
    # at this point no label has dominated newlabel so we add it
    labels.append(newlabel)
    return True
    
class Label:
    resources = []
    # construct an initial label corresponding to an empty path
    def __init__(self):
        # vertex where this partial path is arriving at
        self.at = 0
        # already visited nodes
        self.visited = set()
        # has this label already been extended?
        self.toextend = True
        # predecessor; should point to a Label
        self.pred = self
        self.cost = 0
        self.length = 0
        # resource consumption
        self.q = [0 for x in self.resources]

    # Returns True if self dominates other
    # pre-condition: self.at == other.at
    def dominates(self, other):
        if self.cost > other.cost or self.length > other.length:
            return False
        for s, o in zip(self.q, other.q):
            if s > o:
                return False
        return True

    # Extend label to given vertex
    def extend(self, vertex, rc, d):
        nl = Label()
        nl.at = vertex
        nl.pred = self
        nl.visited = self.visited.union((vertex,))
        nl.cost = self.cost + rc[self.at][vertex]
        nl.length = self.length + d[self.at][vertex]
        # resource is consumed if i^th bit of vertex is 1
        nl.q = [ r + 1 if (vertex & (1 << i) > 0) else r
                 for i, r in enumerate(self.q) ]
        return nl

    def __repr__(self):
        seq = [self.at]
        tmp = self
        while tmp.pred != tmp:
            tmp = tmp.pred
            seq.append(tmp.at)
        seq.reverse()
        return 'Label at node ' + str(self.at) \
            + '\tcost = ' + str(self.cost) + '\tlength = ' + str(self.length) \
            + '\tq = ' + str(self.q) \
            + '\tsequence = ' + str(seq)
