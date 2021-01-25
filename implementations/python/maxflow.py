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
            flow[i][j] = 0.0
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
                if pred[j] == -1 and j != s and cap[cur][j] > flow[cur][j]:
                    pred[j] = cur
                    Q.append(j)
        # did we find an augmenting path?
        if pred[t] != -1:
            df = Inf
            i, j = pred[t], t
            while i != -1:
                if df > cap[i][j] - flow[i][j]:
                    df = cap[i][j] - flow[i][j]
                i, j = pred[i], i
            i, j = pred[t], t
            while i != -1:
                flow[i][j] += df
                i, j = pred[i], i
            totalflow += df
        else:
            moreflow = False
    return totalflow

# taken and slightly adapted from wikipedia
def relabel_to_front(C, F, n, source, sink):
    for i in range(n):
        for j in range(n):
            F[i][j] = 0
    # residual capacity from u to v is C[u][v] - F[u][v]

    height = [0] * n  # height of node
    excess = [0] * n  # flow into node minus flow from node
    seen   = [0] * n  # neighbours seen since last relabel
    # node "queue"
    nodelist = [i for i in range(n) if i != source and i != sink]

    def push(u, v):
        send = min(excess[u], C[u][v] - F[u][v])
        F[u][v] += send
        F[v][u] -= send
        excess[u] -= send
        excess[v] += send

    def relabel(u):
        # Find smallest new height making a push possible,
        # if such a push is possible at all.
        min_height = Inf
        for v in range(n):
            if C[u][v] - F[u][v] > zero:
                min_height = min(min_height, height[v])
                height[u] = min_height + 1

    def discharge(u):
        while excess[u] > zero:
            if seen[u] < n:  # check next neighbour
                v = seen[u]
                if C[u][v] - F[u][v] > zero and height[u] > height[v]:
                    push(u, v)
                else:
                    seen[u] += 1
            else:  # we have checked all neighbours. must relabel
                relabel(u)
                seen[u] = 0

    height[source] = n  # longest path from source to sink is less than n long
    excess[source] = Inf # send as much flow as possible to neighbours of source
    for v in range(n):
        push(source, v)

    p = 0
    while p < len(nodelist):
        u = nodelist[p]
        old_height = height[u]
        discharge(u)
        if height[u] > old_height:
            nodelist.insert(0, nodelist.pop(p))  # move to front of list
            p = 0  # start from front of list
        else:
            p += 1

    return sum(F[source])
