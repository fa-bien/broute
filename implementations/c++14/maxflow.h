#include <deque>

// C is a flat matrix of arc capacities
// F is a flat matrix of flow values
// n is the number of nodes in the complete graph
// s is the source
// t is the sink
double edmondskarp(double *C, double *F, int n, int s, int t) {
    double totalflow = 0.0;
    bool moreflow = true;
    deque<int> Q;
    vector<int> pred(n, -1);
    for (int i=0; i < n; i++) {
        for (int j=0; j < n; j++) {
            F[i*n+j] = 0.0;
        }
    }
    while (moreflow) {
        // reset pred
        for (int i=0; i < n; i++) {
            pred[i] = -1;
        }
        Q.push_back(s);
        while (! Q.empty()) {
            int cur = Q.front();
            Q.pop_front();
            for (int j=0; j < n; j++) {
                if (j == cur) continue;
                if (pred[j] == -1 && j != s && C[cur*n+j] > F[cur*n+j]) {
                    pred[j] = cur;
                    Q.push_back(j);
                }
            }
        }
        // did we find an augmenting path?
        if (pred[t] != -1) {
            double df = 1e12;
            int i = pred[t];
            int j = t;
            while (i != -1) {
                if (df > C[i*n+j] - F[i*n+j]) df = C[i*n+j] - F[i*n+j];
                j = i;
                i = pred[i];
            }
            i = pred[t];
            j = t;
            while (i != -1) {
                F[i*n+j] += df;
                j = i;
                i = pred[i];
            }
            totalflow += df;
        } else {
            moreflow = false;
        }
    }
    return totalflow;
}
