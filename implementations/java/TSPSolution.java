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
	while (first2eimprovement()) t++;
	return t;
    }

    private boolean first2eimprovement() {
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

    public int or_opt() {
	int t = 0;
	while (firstorimprovement()) t++;
	return t;
    }

    private boolean firstorimprovement() {
	for (int i=1; i < nodes_.size() - 1; i++) {
	    for (int l = 1; l < 1 + Math.min(3, nodes_.size() - 1 - i); l++) {
		for (int p=0; p < i-1; p++) {
		    if (or_delta(i, l, p) < 0) {
			// first copy sequence we want to move
			int [] t = new int[l];
			for(int j=0; j < l; j++) { t[j] = nodes_.get(i+j); }
			// next move around what will end up being right of it
			for(int j=i-1; j > p; j--) {
			    nodes_.set(j+l, nodes_.get(j));
			}
			// finally write in the sequence being moved
			for (int j=0; j < l; j++) { nodes_.set(p+1+j, t[j]); }
			return true;
		    }
		}
		for (int p=i+l; p < nodes_.size() - 1; p++) {
		    if (or_delta(i, l, p) < 0) {
			// first copy sequence we want to move
			int [] t = new int[l];
			for(int j=0; j < l; j++) { t[j] = nodes_.get(i+j); }
			// next move around what will end up being left of it
			for(int j=i+l; j <= p; j++) {
			    nodes_.set(j-l, nodes_.get(j));
			}
			// finally write in the sequence being moved
			for (int j=0; j < l; j++) { nodes_.set(p+1+j-l, t[j]); }
			return true;
		    }
		}
	    }
	}
	return false;
    }

    private int or_delta(int i, int l, int p) {
	return data_.d(nodes_.get(i-1), nodes_.get(i+l))
	    + data_.d(nodes_.get(p), nodes_.get(i))
	    + data_.d(nodes_.get(i+l-1), nodes_.get(p+1))
	    - data_.d(nodes_.get(p), nodes_.get(p+1))
	    - data_.d(nodes_.get(i-1), nodes_.get(i))
	    - data_.d(nodes_.get(i+l-1), nodes_.get(i+l));
    }

    public int lns(int niter) {
	int checksum = 0;
	for (int iter=0; iter < niter; iter++) {
	    // step 0: copy solution
	    ArrayList<Integer> tmp = new ArrayList<Integer>(nodes_);
	    ArrayList<Integer> unplanned = new ArrayList<Integer>();
	    // step 1: destroy
	    int where = 1;
	    while (where < tmp.size() - 1) {
		unplanned.add(tmp.get(where));
		tmp.remove(where);
		where += 1;
	    }
	    // step 2: repair
	    while (unplanned.size() > 0) {
		int bestfrom=0, bestto=0;
		int bestcost = Integer.MAX_VALUE;
		for (int k=0; k < unplanned.size(); k++) {
		    for (int to=0; to < tmp.size() - 1; to++) {
			int delta = data_.d(tmp.get(to), unplanned.get(k)) +
			    data_.d(unplanned.get(k), tmp.get(to+1)) -
			    data_.d(tmp.get(to), tmp.get(to+1));
			if (delta < bestcost) {
			    bestcost = delta;
			    bestfrom = k;
			    bestto = to;
			}
			
		    }
		}
		// perform best found insertion
		tmp.add(bestto + 1, unplanned.get(bestfrom));
		unplanned.remove(bestfrom);
		checksum += bestcost;
	    }
	    // step 3: move or not
	    nodes_ = tmp;
	}
	return checksum;
    }

    public int espprc(int nResources, int resourceCapacity) {
        int tourlen = 0;
        for (int i=0; i < nodes_.size() -1; i++) {
	    tourlen += data_.d(nodes_.get(i), nodes_.get(i+1));
        }
        int n = data_.n();
        int[] d = data_.d();
        double[] rc = data_.aux();
	double[] dual = new double[n];
	for (int t=0; t < nodes_.size() - 1; t++) {
	    int i = nodes_.get(t);
	    int j = nodes_.get(t+1);
	    dual[j] = (double) d[i*n+j];
	}
	for (int i=0; i < n; i++) {
	    for (int j=0; j < n; j++) {
		rc[i*n+j] = d[i*n+j] - dual[j];
	    }
	}
	// for the max. length constraint we use the best assignment
	int bestassignment = 0;
	for (int i=0; i < n; i++) {
	    int best = Integer.MAX_VALUE;
	    for (int j=0; j < n; j++) {
		if (i == j) continue;
		if (d[i*n+j] < best) {
		    best = d[i*n+j];
		}
	    }
	    bestassignment += best;
	}
        ESPPRC e = new ESPPRC(n, rc, d, nResources, resourceCapacity,
                              bestassignment);
	return e.solve();
    }
}
