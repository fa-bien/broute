import java.util.ArrayList;
import java.util.Arrays;
import java.util.ArrayDeque;

class LabelWithIndex {
    // where we're at
    private int at_;
    // already visited nodes
    private boolean[] visited_;
    // has this label already been extended?
    private boolean ignore_;
    // predecessor label
    private Integer pred_;
    //
    private double cost_;
    private int length_;
    // resource consumption
    private int[] q_;
    // successors for later recursive deletion when dominated
    private ArrayList<Integer> successors_;


    // number of resources considered
    public static int nresources;

    // number of vertices (also gives dimension of cost/len matrix)
    public static int nnodes;
    
    public LabelWithIndex() {
        at_ = 0;
        visited_ = new boolean[nnodes];
        Arrays.fill(visited_, false);
        ignore_ = false;
        pred_ = -1;
        cost_ = 0.0;
        length_ = 0;
	q_ = new int[nresources];
        Arrays.fill(q_, 0);
        successors_ = new ArrayList<Integer>();
    }
    
    protected boolean dominates (LabelWithIndex other) {
	if (cost_ > other.cost_ || length_ > other.length_) return false;
	for (int i=0; i < nnodes; i++) {
	    if (visited_[i] && ! other.visited_[i]) return false;
	}
	for (int i=0; i < nresources; i++) {
	    if (q_[i] > other.q_[i]) return false;
	}
	return true;
    }

    // constructor by extension
    public LabelWithIndex(double[] rc, int[] d,
                          LabelWithIndex pred, Integer predindex, int to) {
	ignore_ = false;
	at_ = to;
	pred_ = predindex;
	visited_ = new boolean[nnodes];
        System.arraycopy(pred.visited_, 0, visited_, 0, nnodes);
	visited_[to] = true;
	cost_ = pred.cost_ + rc[pred.at_ * nnodes + to];
	length_ = pred.length_ + d[pred.at_ * nnodes + to];
	q_ = new int[nresources];
        System.arraycopy(pred.q_, 0, q_, 0, nresources);
	for (int r=0; r < nresources; r++) {
	    if ((to & (1 << r)) > 0) {
		q_[r] += 1;
	    }
	}
        successors_ = new ArrayList<Integer>();
    }

    protected void addsuccessor(Integer successor) {
	successors_.add(successor);
    }

    // getters
    protected boolean ignore() { return ignore_; }
    protected void setignore() { ignore_ = true; }
    protected boolean visits(int n) { return visited_[n]; }
    protected int length()  { return length_; }
    protected double cost() { return cost_; }
    private int at() { return at_; }
    protected int getrusage(int r) { return q_[r]; }
    Integer predecessor() { return pred_; }
    ArrayList<Integer> successors() { return successors_; }
}

class LabelCollection {
    private ArrayList<LabelWithIndex> labels_;
    
    public LabelCollection() {
        labels_ = new ArrayList<LabelWithIndex>();
    }

    int emptyLabel() {
        labels_.add(new LabelWithIndex());
        return labels_.size() - 1;
    }

    int extend(double[] rc, int[] d, Integer predindex, int to) {
        LabelWithIndex nl = new LabelWithIndex(rc, d,
                                               labels_.get(predindex),
                                               predindex, to);
        labels_.add(nl);
        return labels_.size() - 1;
    }
    
    void addsuccessor(int from, int to) {
        labels_.get(from).addsuccessor(to);
    }
    
    void marksuccessors(int index) {
	for (int s: labels_.get(index).successors()) {
	    setignore(s);
	    marksuccessors(s);
	}
    }

    // update labels with newlabel, i.e. remove dominated elements as needed.
    // return true if newlabel is added, false otherwise
    protected boolean update(ArrayList<Integer> labels, int nlindex) {
	int i=0;
	while (i < labels.size()) {
	    if (labels_.get(labels.get(i)).dominates(labels_.get(nlindex))) {
		return false;
	    }
	    if (labels_.get(nlindex).dominates(labels_.get(labels.get(i)))) {
		marksuccessors(labels.get(i));
		if (i < labels.size() - 1) {
		    labels.set(i, labels.get(labels.size()-1));
		}
		labels.remove(labels.size()-1);
	    } else {
		i += 1;
	    }
	}
	// at this point newlabel is not dominated so we add it
	labels.add(nlindex);
	return true;
    }

    // getters
    protected boolean ignore(int lindex) {
        return labels_.get(lindex).ignore(); }
    protected void setignore(int lindex) { labels_.get(lindex).setignore(); }
    protected boolean visits(int lindex, int n) {
        return labels_.get(lindex).visits(n); }
    protected int length(int lindex)  { return labels_.get(lindex).length(); }
    protected double cost(int lindex) { return labels_.get(lindex).cost(); }
    protected int getrusage(int lindex, int r) {
        return labels_.get(lindex).getrusage(r); }
}

public class ESPPRCLC extends ESPPRC {
    public ESPPRCLC(int nnodes, double[] rc, int[] d,
                    int nresources, int rescap, int maxlen) {
        super(nnodes, rc, d, nresources, rescap, maxlen);
    }
    
    public double solve(){
	// set class variables
	LabelWithIndex.nresources = nresources_;
	LabelWithIndex.nnodes = nnodes_;
	// initial label (empty path) and queue
        LabelCollection lc = new LabelCollection();
	int l0 = lc.emptyLabel();
	ArrayDeque<Integer> Q = new ArrayDeque<Integer> ();
	boolean[] inQ = new boolean[nnodes_];
        Arrays.fill(inQ, false);
	Q.addLast(0);
	inQ[0] = true;
        ArrayList<ArrayList<Integer>> labels =
            new ArrayList<ArrayList<Integer>>(nnodes_);
        for (int i=0; i < nnodes_; i++) {
            labels.add(new ArrayList<Integer>());
        }
	labels.get(0).add(l0);
	// main DP loop
	while (Q.size() > 0) {
	    int n = Q.pollFirst();
	    inQ[n] = false;
	    for (int lindex: labels.get(n)) {
		if (lc.ignore(lindex)) {
		    continue;
		}
		for (int succ = 0; succ < nnodes_; succ++) {
		    if (lc.visits(lindex, succ) || succ == n) {
			continue;
		    }
                    // succ is a candidate for extension; is it length-feasible?
                    if (lc.length(lindex)
			+ d_[n*nnodes_+succ] + d_[succ*nnodes_] > maxlen_) {
			continue;
		    }
		    // is it resource-feasible ?
		    boolean rfeas = true;
		    for (int i=0; i < nresources_; i++) {
			if ( (succ & (1 << i)) > 0 &&
			     lc.getrusage(lindex, i) + 1 > resourcecapacity_ ) {
			    rfeas = false;
			    break;
			}
		    }
		    if (! rfeas) {
			continue;
		    }
		    // at this point we know the extension is feasible
		    int nl = lc.extend(rc_, d_, lindex, succ);
		    boolean added = lc.update(labels.get(succ), nl);
		    if (added) lc.addsuccessor(lindex, nl);
		    if (added && (! inQ[succ]) && succ != 0) {
			Q.addLast(succ);
			inQ[succ] = true;
		    }
		}
		lc.setignore(lindex);
	    }
	}
	double bestcost = lc.cost(labels.get(0).get(0));
	for (int i=1; i < labels.get(0).size(); i++) {
	    if (lc.cost(labels.get(0).get(i)) < bestcost) {
                bestcost = lc.cost(labels.get(0).get(i));
	    }
	}
	return bestcost;
    }
}
