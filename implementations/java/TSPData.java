public class TSPData {
    private int n_;
    private int[] d_;
    // auxiliary graph used for espprc and maxflow
    private double[] aux_;
    
    // here be getters
    public int d(int i, int j) {
	return d_[i*n_+j];
    }
    public int n() { return n_; }
    public int[] d() { return d_; }
    public double[] aux() { return aux_; }
    
    public TSPData(int n, int[]d) {
	n_ = n;
	d_ = d;
        aux_ = new double[n*n];
    }
}
