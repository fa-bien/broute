public class TSPData {
    private int n_;
    private int[] d_;

    // here be getters
    public int d(int i, int j) {
	return d_[i*n_+j];
    }
    public int n() { return n_; }

    public TSPData(int n, int[]d) {
	n_ = n;
	d_ = d;
    }
}
