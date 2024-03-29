public class TSPData {
    private int n_;
    private int[][] d_;

    // here be getters
    public int d(int i, int j) {
	return d_[i][j];
    }
    public int n() { return n_; }

    public TSPData(int n, int[][]d) {
	n_ = n;
	d_ = d;
    }
    
    public TSPData(int n, int[]d) {
	n_ = n;
	d_ = new int[n][n];
	for (int i=0; i<n; i++) {
	    for (int j=0; j<n; j++) {
		d_[i][j] = d[i*n+j];
	    }
	}
    }
}
