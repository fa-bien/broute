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
	while (first2eimprovement()) t++;
	return t;
    }

    private boolean first2eimprovement() {
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

    public int or_opt() {
	int t = 0;
	while (firstorimprovement()) t++;
	return t;
    }

    private boolean firstorimprovement() {
	for (int i=1; i < nodes_.length - 1; i++) {
	    for (int l = 1; l < 1 + Math.min(3, nodes_.length - 1 - i); l++) {
		for (int p=0; p < i-1; p++) {
		    if (or_delta(i, l, p) < 0) {
			// first copy sequence we want to move
			int [] t = new int[l];
			for(int j=0; j < l; j++) { t[j] = nodes_[i+j]; }
			// next move around what will end up being right of it
			for(int j=i-1; j > p; j--) { nodes_[j+l] = nodes_[j]; }
			// finally write in the sequence being moved
			for (int j=0; j < l; j++) { nodes_[p+1+j] = t[j]; }
			return true;
		    }
		}
		for (int p=i+l; p < nodes_.length - 1; p++) {
		    if (or_delta(i, l, p) < 0) {
			// first copy sequence we want to move
			int [] t = new int[l];
			for(int j=0; j < l; j++) { t[j] = nodes_[i+j]; }
			// next move around what will end up being left of it
			for(int j=i+l; j <= p; j++) { nodes_[j-l] = nodes_[j]; }
			// finally write in the sequence being moved
			for (int j=0; j < l; j++) { nodes_[p+1+j-l] = t[j]; }
			return true;
		    }
		}
	    }
	}
	return false;
    }

    private int or_delta(int i, int l, int p) {
	return data_.d(nodes_[i-1], nodes_[i+l])
	    + data_.d(nodes_[p], nodes_[i])
	    + data_.d(nodes_[i+l-1], nodes_[p+1])
	    - data_.d(nodes_[p], nodes_[p+1])
	    - data_.d(nodes_[i-1], nodes_[i])
	    - data_.d(nodes_[i+l-1], nodes_[i+l]);
    }
}
