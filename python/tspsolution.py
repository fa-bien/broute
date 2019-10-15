import tspdata
import copy

class TSPSolution:
    def __init__(self, data, permutation):
        self.data = data
        self.nodes = copy.copy(permutation)

    def two_opt(self):
        t = 0
        while self.firstimprovement():
            t += 1
        return t

    def firstimprovement(self):
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
