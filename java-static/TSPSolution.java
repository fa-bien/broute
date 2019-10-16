import java.util.Arrays;

public class TSPSolution {
    private TSPData data_;
    private int[] nodes_;

    public TSPSolution(TSPData data, int[] nodes) {
	data_ = data;
	nodes_ = nodes.clone();
    }
    
    public int two_opt() {
	int t = 0;
	while (first_improvement()) t++;
	return t;
    }

    private boolean first_improvement() {
	for (int p1=0; p1 < nodes_.length- 3; p1++) {
	    for (int p2=p1+2; p2 < nodes_.length -1; p2++) {
		if (data_.d(nodes_[p1], nodes_[p1+1]) +
		    data_.d(nodes_[p2], nodes_[p2+1]) > 
		    data_.d(nodes_[p1], nodes_[p2]) +
		    data_.d(nodes_[p1+1], nodes_[p2+1])) {
		    // improving two-exchange found!
		    int t;
		    for (int i=0; i < (p2-p1+1) / 2; i++) {
			t = nodes_[p1+1+i];
			nodes_[p1+1+i] = nodes_[p2-i];
			nodes_[p2-i] = t;
		    }
		    return true;
		}
	    }
	}
	return false;
    }
}
