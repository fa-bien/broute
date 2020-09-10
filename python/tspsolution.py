import tspdata
import copy
from itertools import chain

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
                        t = [ x for x in self.nodes[i:i+l] ]
                        if i < p:
                            # shift stuff left
                            for j in range(i, p-l+1):
                                self.nodes[j] = self.nodes[j+l]
                            # copy sequence right of the stuff 
                            for j in range(l):
                                self.nodes[p+1+j-l] = t[j]
                        else:
                            # shift stuff right
                            for j in range(i-1, p, -1):
                                self.nodes[j+l] = self.nodes[j]
                            # copy sequence right of the stuff 
                            for j in range(l):
                                self.nodes[p+1+j] = t[j]
                        return True
        return False

    # old implementation, similar time performance but more allocations
    # def firstorimprovement(self):
    #     # actually speeds things up!
    #     tour, d = self.nodes, self.data.d
    #     for i in range(1, len(tour) - 1):
    #         for l in range(1, 1 + min(3, len(tour)-1-i)):
    #             for pos in chain(range(i-1), range(i+l, len(tour)-1)):
    #                 delta = d[tour[i-1]][tour[i+l]] + d[tour[pos]][tour[i]] + \
    #                     d[tour[i+l-1]][tour[pos+1]] - d[tour[pos]][tour[pos+1]]\
    #                     - d[tour[i-1]][tour[i]] - d[tour[i+l-1]][tour[i+l]]
    #                 # perform improving move
    #                 if delta < 0:
    #                     if i < pos:
    #                         self.nodes = self.nodes[:i] + \
    #                             self.nodes[i+l:pos+1] + \
    #                             self.nodes[i:i+l] + \
    #                             self.nodes[pos+1:]
    #                     else:
    #                         self.nodes = self.nodes[0:pos+1] + \
    #                             self.nodes[i:i+l] + \
    #                             self.nodes[pos+1:i] + \
    #                             self.nodes[i+l:]
    #                     return True
    #     return False
    
    def cost(self):
        total = 0
        for i, j in zip(self.nodes[:-1], self.nodes[1:]):
            total += self.data.d[i][j]
        return total
