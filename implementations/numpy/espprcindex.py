import collections

import numpy as np

import espprc

class LabelWithIndex(espprc.Label):
    # construct an initial label corresponding to an empty path
    def __init__(self):
        # vertex where this partial path is arriving at
        self.at = 0
        # already visited nodes
        self.visited = set()
        # has this label already been extended?
        self.ignore = False
        # predecessor; should point to a Label
        self.pred = -1
        self.cost = 0
        self.length = 0
        # resource consumption
        self.q = np.array([0 for x in self.resources])
        # successors for later recursive deletion when dominated
        self.successors = []

    # Extend label to given vertex
    def extend(self, rc, d, predindex, vertex):
        nl = LabelWithIndex()
        nl.at = vertex
        nl.pred = predindex
        nl.visited = self.visited.union((vertex,))
        nl.cost = self.cost + rc[self.at,vertex]
        nl.length = self.length + d[self.at,vertex]
        # resource is consumed if i^th bit of vertex is 1
        nl.q = np.array([ r + 1 if (vertex & (1 << i) > 0) else r
                          for i, r in enumerate(self.q) ])
        return nl

    def __repr__(self):
        return 'Label at node ' + str(self.at) \
            + '\tcost = ' + str(self.cost) + '\tlength = ' + str(self.length) \
            + '\tq = ' + str(self.q)
    
class LabelCollection:
    def __init__(self):
        self.labels = []
        
    def marksuccessors(self, lindex):
        for s in self.labels[lindex].successors:
            self.labels[s].ignore = True
            self.marksuccessors(s)

    # * compare newlabel with collection of labels removing dominated labels as
    #   necessary
    # * adds newlabel to collection labels if it is not dominated
    # * returns true if newlabel was added
    def updatedominance(self, labels, nlindex):
        i = 0
        while i < len(labels):
            if self.labels[labels[i]].dominates(self.labels[nlindex]):
                return False
            elif self.labels[nlindex].dominates(self.labels[labels[i]]):
                self.marksuccessors(labels[i])
                if i < len(labels) - 1:
                    labels[i] = labels[-1]
                del labels[-1]
            else:
                i += 1
        # at this point no label has dominated newlabel so we add it
        labels.append(nlindex)
        return True

    def emptylabel(self):
        self.labels.append(LabelWithIndex())
        return len(self.labels) - 1

    # extend label at index 'fro' to node 'to'
    def extend(self, rc, d, fro, to):
        self.labels.append(self.labels[fro].extend(rc, d, fro, to))
        return len(self.labels) - 1
    
class ESPPRCLC(espprc.ESPPRC):
    def solve(self):
        # initialise DP data: list of labels, queue, initial label, resources
        vertices = np.array([ x for x in range(self.n) ])
        Q, Qset = collections.deque(), set([0])
        Q.append(0)
        labels = [ [] for x in vertices ]
        LabelWithIndex.resources = np.array([x for x in range(self.nresources)])
        # label collection
        lc = LabelCollection()
        l0 = lc.emptylabel()
        labels[0].append(l0)
        # step 3: run DP
        while len(Qset) > 0:
            n = Q.popleft()
            Qset.remove(n)
            for lindex in labels[n]:
                label = lc.labels[lindex]
                if label.ignore:
                    continue
                for succ in vertices:
                    if succ in label.visited or succ == n: continue
                    # succ is a candidate for extension; is it length-feasible?
                    if label.length + self.d[n,succ] + self.d[succ,0] \
                       > self.maxlen:
                        continue
                    # is it resource-feasible?
                    rfeas = True
                    for i, r in enumerate(label.q):
                        if (succ & (1 << i) > 0) and r + 1 > self.rescap:
                            rfeas = False
                            break
                    if not rfeas: continue
                    # now we can actually extend the label!
                    nl = lc.extend(self.rc, self.d, lindex, succ)
                    # Let's update dominance
                    added = lc.updatedominance(labels[succ], nl)
                    if added:
                        label.successors.append(nl)
                    if added and not (succ in Qset) and succ != 0:
                        Qset.add(succ)
                        Q.append(succ)
                label.ignore = True
        # step 4: return distance of cheapest label as hash value.
        return min(lc.labels[l].cost for l in labels[0])
