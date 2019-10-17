import java.util.ArrayList;
import java.util.Arrays;

public class TSPSolution {
    private TSPData data_;
    private ArrayList<Integer> nodes_;

    public TSPSolution(TSPData data, ArrayList<Integer> nodes) {
	data_ = data;
	nodes_ = nodes;
    }
    
    public int two_opt() {
	int t = 0;
	while (first_improvement()) t++;
	return t;
    }

    private boolean first_improvement() {
	for (int p1=0; p1 < nodes_.size() - 3; p1++) {
	    for (int p2=p1+2; p2 < nodes_.size() -1; p2++) {
		if (data_.d(nodes_.get(p1), nodes_.get(p1+1)) +
		    data_.d(nodes_.get(p2), nodes_.get(p2+1)) > 
		    data_.d(nodes_.get(p1), nodes_.get(p2)) +
		    data_.d(nodes_.get(p1+1), nodes_.get(p2+1))) {
		    // improving two-exchange found!
		    int t;
		    for (int i=0; i < (p2-p1+1) / 2; i++) {
			t = nodes_.get(p1+1+i);
			nodes_.set(p1+1+i, nodes_.get(p2-i));
			nodes_.set(p2-i, t);
		    }
		    return true;
		}
	    }
	}
	return false;
    }
}
