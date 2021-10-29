import random
import math

mapsize = 100


# encapsulate TSP data: instance + starting solutions to optimise for
# benchmarking purpose
class TSPData:
    def __init__(self, n=0, d=[], filename=None):
        if filename is None:
            self.n, self.d = n, d
        else:
            self.loadVRPLIB(filename)
        # auxiliary graph used e.g. for storing reduced costs (espprc)
        # or flow values (maxflow)
        # Typically it is used many times but only needs to be allocated once
        # and represents some kind of input data, therefore this is a good
        # place to have it.
        # dummy values to begin with...
        self.aux = [[float(x) for x in row] for row in d]
        # second auxiliary graph used to store results e.g. for maxflow
        self.aux2 = [[0.0 for x in row] for row in d]

    def matrixstring(self):
        rows = [' '.join(str(x) for x in row) for row in self.d]
        return '\n'.join(rows)

    def genrandom(self, n):
        x = [random.choice(range(mapsize)) for x in range(n)]
        y = [random.choice(range(mapsize)) for x in range(n)]
        self.n = n
        # Euclidean distances
        self.d = [[int(math.hypot(x[i]-x[j], y[i]-y[j]) * 100)
                   for j in range(n)] for i in range(n)]
        # triangle inequality correction
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                for k in range(n):
                    if i == k or j == k:
                        continue
                    if self.d[i][j] + self.d[j][k] < self.d[i][k]:
                        self.d[i][k] = self.d[i][j] + self.d[j][k]

    def loadVRPLIB(self, filename):
        n = 0
        x, y = [], []
        state = 'header'
        with open(filename, 'r') as f:
            for line in f:
                if state == 'header':
                    if line.startswith('DIMENSION : '):
                        n = int(line.split()[2])
                    elif line.startswith('NODE_COORD_SECTION'):
                        state = 'nodes'
                    else:
                        pass
                elif state == 'nodes':
                    if line.startswith('DEMAND_SECTION'):
                        state = 'done'
                    else:
                        toks = line.split()
                        i, u, v = int(toks[0]), float(toks[1]), float(toks[2])
                        x.append(u)
                        y.append(v)
                        assert i == len(x), 'incorrect index in VRPLIB file'
                else:
                    pass
        # Euclidean distances
        self.n = n
        self.d = [[int(math.hypot(x[i]-x[j], y[i]-y[j]) * 100)
                   for j in range(n)] for i in range(n)]

        for u, v in zip(x, y):
            print(u, v)
                        
    def genrandomcycle(self):
        # solution generation: random permutations
        # solutions always start and end with zero
        points = [x for x in range(1, self.n)]
        random.shuffle(points)
        return [0] + points + [0]
