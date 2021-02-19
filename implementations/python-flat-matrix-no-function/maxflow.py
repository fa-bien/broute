import sys
import collections

Inf = 100000
zero = 0

# cap[i][j] is the capacity of arc (i, j)
# flow[i][j]g is where we store the flow from i to j
# n is the number of nodes in the complete graph
# s is the source
# t is the sink
def edmondskarp(cap, flow, n, s, t):
    totalflow = 0.0
    moreflow = True
    Q = collections.deque()
    pred = [ -1 for i in range(n) ]
    for i in range(n):
        for j in range(n):
            flow[i*n+j] = 0.0
    while moreflow:
        # reset pred
        for i in range(n):
            pred[i] = -1
        Q.append(s)
        while len(Q) > 0:
            cur = Q.popleft()
            for j in range(n):
                if j == cur:
                    continue
                if pred[j] == -1 and j != s and cap[cur*n+j] > flow[cur*n+j]:
                    pred[j] = cur
                    Q.append(j)
        # did we find an augmenting path?
        if pred[t] != -1:
            df = Inf
            i, j = pred[t], t
            while i != -1:
                if df > cap[i*n+j] - flow[i*n+j]:
                    df = cap[i*n+j] - flow[i*n+j]
                i, j = pred[i], i
            i, j = pred[t], t
            while i != -1:
                flow[i*n+j] += df
                i, j = pred[i], i
            totalflow += df
        else:
            moreflow = False
    return totalflow
