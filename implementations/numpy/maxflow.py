import sys
import collections

import numpy as np

Inf = 100000

# cap[i][j] is the capacity of arc (i, j)
# flow[i][j]g is where we store the flow from i to j
# n is the number of nodes in the complete graph
# s is the source
# t is the sink
def edmondskarp(cap, flow, n, s, t):
    totalflow = 0.0
    moreflow = True
    Q = collections.deque()
    pred = np.array([ -1 for i in range(n) ])
    
    for i in range(n):
        for j in range(n):
            flow[i,j] = 0.0
    # flow.fill(0.0)
            
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
                if pred[j] == -1 and j != s and cap[cur,j] > flow[cur,j]:
                    pred[j] = cur
                    Q.append(j)
        # did we find an augmenting path?
        if pred[t] != -1:
            df = Inf
            i, j = pred[t], t
            while i != -1:
                if df > cap[i,j] - flow[i,j]:
                    df = cap[i,j] - flow[i,j]
                i, j = pred[i], i
            i, j = pred[t], t
            while i != -1:
                flow[i,j] += df
                i, j = pred[i], i
            totalflow += df
        else:
            moreflow = False
    return totalflow
