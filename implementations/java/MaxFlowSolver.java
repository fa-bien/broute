import java.util.ArrayDeque;
import java.util.Arrays;

class MaxFlowSolver {
    // capacity graph
    private double[] C_;
    // flow graph
    private double[] F_;
    //number of nodes in the complete graphs
    private int n_;

    public MaxFlowSolver(double[] C, double[] F, int n) {
        C_ = C;
        F_ = F;
        n_ = n;
    }
    
    // s is the source, t is the sink
    public double edmondsKarp(int s, int t) {
        double totalflow = 0;
        boolean moreflow = true;
	ArrayDeque<Integer> Q = new ArrayDeque<Integer> ();
        int[] pred = new int[n_];
        Arrays.fill(pred, -1);
        for (int i=0; i < n_; i++) {
            for (int j=0; j < n_; j++) {
                F_[i*n_+j] = 0.0;
            }
        }
        while (moreflow) {
            // reset predecessors
            for (int i=0; i < n_; i++) {
                pred[i] = -1;
            }
            Q.addLast(s);
            while (Q.size() > 0) {
                int cur = Q.pollFirst();
                for (int j=0; j < n_; j++) {
                    if (j == cur) continue;
                    if (pred[j] == -1 && j != s && C_[cur*n_+j] > F_[cur*n_+j]){
                        pred[j] = cur;
                        Q.addLast(j);
                    }
                }
            }
            // did we find an augmenting path?
            if (pred[t] != -1) {
                double df = Double.MAX_VALUE;
                int i = pred[t];
                int j = t;
                while (i != -1) {
                    if (df > C_[i*n_+j] - F_[i*n_+j]) {
                        df = C_[i*n_+j] - F_[i*n_+j];
                    }
                    j = i;
                    i = pred[i];
                }
                i = pred[t];
                j = t;
                while (i != -1) {
                    F_[i*n_+j] += df;
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
}
