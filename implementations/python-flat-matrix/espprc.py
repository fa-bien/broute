import collections

class Label:
    resources = []
    # construct an initial label corresponding to an empty path
    def __init__(self):
        # vertex where this partial path is arriving at
        self.at = 0
        # already visited nodes
        self.visited = set()
        # has this label already been extended?
        self.ignore = False
        # predecessor; should point to a Label
        self.pred = self
        self.cost = 0
        self.length = 0
        # resource consumption
        self.q = [0 for x in self.resources]
        # successors for later recursive deletion when dominated
        self.successors = []

    # Returns True if self dominates other
    # pre-condition: self.at == other.at
    def dominates(self, other):
        if self.cost > other.cost or self.length > other.length:
            return False
        for v in self.visited:
            if not v in other.visited:
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
        nl.cost = self.cost + rc(self.at, vertex)
        nl.length = self.length + d(self.at, vertex)
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

    def marksuccessors(self):
        for s in self.successors:
            s.ignore = True
            s.marksuccessors()

# * compare newlabel with collection of labels removing dominated labels as
#   necessary
# * adds newlabel to collection labels if it is not dominated
# * returns true if newlabel was added
def updatedominance(labels, newlabel):
    i = 0
    while i < len(labels):
        if labels[i].dominates(newlabel):
            return False
        elif newlabel.dominates(labels[i]):
            labels[i].marksuccessors()
            if i < len(labels) - 1:
                labels[i] = labels[-1]
            del labels[-1]
        else:
            i += 1
    # at this point no label has dominated newlabel so we add it
    labels.append(newlabel)
    return True
    
class ESPPRC:
    def __init__(self, n, d, rc, tour, nresources, resourcecapacity, maxlen):
        self.n = n
        self.d = d
        self.rc = rc
        self.nresources = nresources
        self.rescap = resourcecapacity
        self.maxlen = maxlen
        
    def solve(self):
        # initialise DP data: list of labels, queue, initial label, resources
        vertices = [ x for x in range(self.n) ]
        Q, Qset = collections.deque(), set([0])
        Q.append(0)
        labels = [ [] for x in vertices ]
        Label.resources = [ x for x in range(self.nresources) ]
        labels[0].append(Label())
        # step 3: run DP
        while len(Qset) > 0:
            n = Q.popleft()
            Qset.remove(n)
            for label in labels[n]:
                if label.ignore:
                    continue
                for succ in vertices:
                    if succ in label.visited or succ == n: continue
                    # succ is a candidate for extension; is it length-feasible?
                    if label.length + self.d(n, succ) + self.d(succ, 0) \
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
                    nl = label.extend(succ, self.rc, self.d)
                    # Let's update dominance
                    added = updatedominance(labels[succ], nl)
                    if added:
                        label.successors.append(nl)
                    if added and not (succ in Qset) and succ != 0:
                        Qset.add(succ)
                        Q.append(succ)
                label.ignore = True
        # step 4: return distance of cheapest label as hash value.
        return min(label.cost for label in labels[0])
