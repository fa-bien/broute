import java.util.ArrayList;
import java.util.Arrays;
import java.util.ArrayDeque;

class Label {
    // where we're at
    private int at_;
    // already visited nodes
    private boolean[] visited_;
    // has this label already been extended?
    private boolean ignore_;
    // predecessor label
    private Label pred_;
    //
    private double cost_;
    private int length_;
    // resource consumption
    private int[] q_;
    // successors for later recursive deletion when dominated
    private ArrayList<Label> successors_;


    // number of resources considered
    public static int nresources;

    // number of vertices (also gives dimension of cost/len matrix)
    public static int nnodes;
    
    public Label() {
        at_ = 0;
        visited_ = new boolean[nnodes];
        Arrays.fill(visited_, false);
        ignore_ = false;
        pred_ = null;
        cost_ = 0.0;
        length_ = 0;
	q_ = new int[nresources];
        Arrays.fill(q_, 0);
        successors_ = new ArrayList<Label>();
    }
    
    private boolean dominates (Label other) {
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
    public Label(Label pred, int vertex, double[] rc, int[] d) {
	ignore_ = false;
	at_ = vertex;
	pred_ = pred;
	visited_ = new boolean[nnodes];
        System.arraycopy(pred.visited_, 0, visited_, 0, nnodes);
	visited_[vertex] = true;
	cost_ = pred.cost_ + rc[pred.at_ * nnodes + vertex];
	length_ = pred.length_ + d[pred.at_ * nnodes + vertex];
	q_ = new int[nresources];
        System.arraycopy(pred_.q_, 0, q_, 0, nresources);
	for (int r=0; r < nresources; r++) {
	    if ((vertex & (1 << r)) > 0) {
		q_[r] += 1;
	    }
	}
        successors_ = new ArrayList<Label>();
    }

    protected void addsuccessor(Label successor) {
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
    Label predecessor() { return pred_; }
    ArrayList<Label> successors() { return successors_; }
    
    void marksuccessors() {
	for (int s=0; s < successors_.size(); s++) {
	    successors_.get(s).ignore_ = true;
	    successors_.get(s).marksuccessors();
	}
    }

    // update labels with newlabel, i.e. remove dominated elements as needed.
    // return true if newlabel is added, false otherwise
    protected static boolean update(ArrayList<Label> labels, Label newlabel) {
	int i=0;
	while (i < labels.size()) {
	    if (labels.get(i).dominates(newlabel)) {
		return false;
	    }
	    if (newlabel.dominates(labels.get(i))) {
		labels.get(i).marksuccessors();
		if (i < labels.size() - 1) {
		    labels.set(i, labels.get(labels.size()-1));
		}
		labels.remove(labels.size()-1);
	    } else {
		i += 1;
	    }
	}
	// at this point newlabel is not dominated so we add it
	labels.add(newlabel);
	return true;
    }
}

public class ESPPRC {

    protected int nnodes_;
    // reduced cost flat matrix
    protected double[] rc_;
    // length flat matrix
    protected int[] d_;
    // number of resources considered for resource constraints
    protected int nresources_;
    // capacity for each resource
    protected int resourcecapacity_;
    // maximum length for any given tour
    protected int maxlen_;
    
    public ESPPRC(int nnodes, double[] rc, int[] d,
                  int nresources, int rescap, int maxlen) {
	nnodes_ = nnodes;
	d_ = d;
	rc_ = rc;
	nresources_ = nresources;
	resourcecapacity_ = rescap;
	maxlen_ = maxlen;
    }

    public int solve(){
	// set class variables
	Label.nresources = nresources_;
	Label.nnodes = nnodes_;
	// initial label (empty path) and queue
	Label l = new Label();
	ArrayDeque<Integer> Q = new ArrayDeque<Integer> ();
	boolean[] inQ = new boolean[nnodes_];
        Arrays.fill(inQ, false);
	Q.addLast(0);
	inQ[0] = true;
        ArrayList<ArrayList<Label>> labels =
            new ArrayList<ArrayList<Label>>(nnodes_);
        for (int i=0; i < nnodes_; i++) {
            labels.add(new ArrayList<Label>());
        }
	labels.get(0).add(l);
	// main DP loop
	while (Q.size() > 0) {
	    int n = Q.pollFirst();
	    inQ[n] = false;
	    for (Label label: labels.get(n)) {
		if (label.ignore()) {
		    continue;
		}
		for (int succ = 0; succ < nnodes_; succ++) {
		    if (label.visits(succ) || succ == n) {
			continue;
		    }
                    // succ is a candidate for extension; is it length-feasible?
                    if (label.length()
			+ d_[n*nnodes_+succ] + d_[succ*nnodes_] > maxlen_) {
			continue;
		    }
		    // is it resource-feasible ?
		    boolean rfeas = true;
		    for (int i=0; i < nresources_; i++) {
			if ( (succ & (1 << i)) > 0 &&
			     label.getrusage(i) + 1 > resourcecapacity_ ) {
			    rfeas = false;
			    break;
			}
		    }
		    if (! rfeas) {
			continue;
		    }
		    // at this point we know the extension is feasible
		    Label nl = new Label(label, succ, rc_, d_);
		    boolean added = Label.update(labels.get(succ), nl);
		    if (added) label.addsuccessor(nl);
		    if (added && (! inQ[succ]) && succ != 0) {
			Q.addLast(succ);
			inQ[succ] = true;
		    }
		}
		label.setignore();
	    }
	}
	double bestcost = labels.get(0).get(0).cost();
	for (int i=1; i < labels.get(0).size(); i++) {
	    if (labels.get(0).get(i).cost() < bestcost) {
		bestcost = labels.get(0).get(i).cost();
	    }
	}
	return (int) bestcost;
    }
}
