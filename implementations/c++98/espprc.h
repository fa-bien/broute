#ifndef ESPPRC_H
#define ESPPRC_H

#include <vector>
#include <iostream>
#include <set>
#include <deque>
#include <memory>
#include<cstring>

using namespace std;

template <class T> class Label {
protected:
    // where we're at
    int at_;
    // already visited nodes
    bool *visited_;
    // has this label already been extended?
    bool ignore_;
    // predecessor label
    Label<T> *pred_;
    //
    double cost_;
    T length_;
    // resource consumption
    int *q_;
    // successors for later recursive deletion when dominated
    vector<Label<T>*> successors_;

public:

    // number of resources considered
    static int nresources;

    // number of vertices (also gives dimension of cost/len matrix)
    static int nnodes;

    // create an initial dummy label
    Label() {
        at_ = 0;
	visited_ = new bool[nnodes]();
        ignore_ = false;
	pred_ = NULL;
        cost_ = 0.0;
        length_ = 0;
	q_ = new int[nresources]();
	successors_ = vector<Label<T>*>(0);
    }
    
    const bool dominates (const Label<T> &other) const {
	if (cost_ > other.cost_ || length_ > other.length_) return false;
	for(int i=0; i < nnodes; i++) {
	    if (visited_[i] && ! other.visited_[i]) return false;
	}
	for (int i=0; i < nresources; i++) {
	    if (q_[i] > other.q_[i]) return false;
	}
	return true;
    }

    // constructor by extension
    Label(Label<T> *pred, int vertex, double *rc, const T *d) {
	ignore_ = false;
	at_ = vertex;
	pred_ = pred;
	visited_ = new bool[nnodes];
        memcpy(visited_, pred->visited_, nnodes * sizeof(bool));
	visited_[vertex] = true;
	cost_ = pred->cost_ + rc[pred->at_ * nnodes + vertex];
	length_ = pred->length_ + d[pred->at_ * nnodes + vertex];
	q_ = new int[nresources];
        memcpy(q_, pred_->q_, nresources * sizeof(int));
	for (int r=0; r < nresources; r++) {
	    if ((vertex & (1 << r)) > 0) {
		q_[r] += 1;
	    }
	}
    }

    void addsuccessor(Label<T> *successor) {
	successors_.push_back(successor);
    }

    bool ignore() const { return ignore_; }
    void setignore() { ignore_ = true; }

    bool visits(int n) const { return visited_[n]; }

    T length() const { return length_; }
    double cost() const { return cost_; }
    int at() const { return at_; }

    int getrusage(int r) const { return q_[r]; }

    Label<T> *predecessor() const { return pred_; }
    vector<Label<T>*> successors() const { return successors_; }
    
    void marksuccessors() {
	for (unsigned int s=0; s < successors_.size(); s++) {
	    successors_[s]->ignore_ = true;
	    successors_[s]->marksuccessors();
	}
    }

    // update labels with newlabel, i.e. remove dominated elements as needed.
    // return true if newlabel is added, false otherwise
    static bool update(vector<Label<T>*> &labels,
		       Label<T> *newlabel) {
	unsigned int i=0;
	while (i < labels.size()) {
	    if (labels[i]->dominates(*newlabel)) {
		return false;
	    }
	    if (newlabel->dominates(*(labels[i]))) {
		labels[i]->marksuccessors();
		if (i < labels.size() - 1) {
		    labels[i] = labels.back();
		}
		labels.pop_back();
	    } else {
		i += 1;
	    }
	}
	// at this point newlabel is not dominated so we add it
	labels.push_back(newlabel);
	return true;
    }
};

template<class T>
ostream& operator<<(ostream &os, const Label<T> &l) {
    os << "Label at node " << l.at() << "\tcost = " << l.cost()
       << "\tlength = " << l.length() << "\trusage:";
    for (int i=0; i < Label<T>::nresources; i++) {
	os << " " << l.getrusage(i);
    }
    os << "\tvisited:";
    for (int i=0; i < Label<T>::nnodes; i++) {
	if (l.visits(i)) { cout << " " << i; }
    }
    os << "\tignore = " << l.ignore()
       << "\t successors: " << l.successors().size();
    return os;
}

// it's 2020, C++ still requires global definition of class variables
// this is why we can't have nice things
template<class T> int Label<T>::nresources = 0;
template<class T> int Label<T>::nnodes = 0;

template <class T> class ESPPRC {
protected:
    int nnodes_;
    // reduced cost flat matrix
    double *rc_;
    // length flat matrix
    const T *d_;
    // number of resources considered for resource constraints
    int nresources_;
    // capacity for each resource
    int resourcecapacity_;
    // maximum length for any given tour
    T maxlen_;
    
public:
    ESPPRC(int nnodes, double *rc, const T *d,
	   int nresources, int rescap, T maxlen) {
	nnodes_ = nnodes;
	d_ = d;
	rc_ = rc;
	nresources_ = nresources;
	resourcecapacity_ = rescap;
	maxlen_ = maxlen;
    }

    double solve(){
	// set class variables
	Label<T>::nresources = nresources_;
	Label<T>::nnodes = nnodes_;
	// initial label (empty path) and queue
	Label<T> *l = new Label<T>();
	deque<int> Q;
        bool *inQ = new bool[nnodes_]();
	Q.push_back(0);
	inQ[0] = true;
	vector<Label<T>*> *labels = new vector<Label<T>*>[nnodes_]();
        //(nnodes_, vector<shared_ptr<Label<T>>>(0));
	labels[0].push_back(l);
	// main DP loop
	while (! Q.empty()) {
	    int n = Q.front();
	    Q.pop_front();
	    inQ[n] = false;
	    for (unsigned int lindex=0; lindex < labels[n].size(); lindex++) {
                Label<T> *label = labels[n][lindex];
		if (label->ignore()) {
		    continue;
		}
		for (int succ = 0; succ < nnodes_; succ++) {
		    if (label->visits(succ) || succ == n) {
			continue;
		    }
                    // succ is a candidate for extension; is it length-feasible?
                    if (label->length()
			+ d_[n*nnodes_+succ] + d_[succ*nnodes_] > maxlen_) {
			continue;
		    }
		    // is it resource-feasible ?
		    bool rfeas = true;
		    for (int i=0; i < nresources_; i++) {
			if ( (succ & (1 << i)) > 0 &&
			     label->getrusage(i) + 1 > resourcecapacity_ ) {
			    rfeas = false;
			    break;
			}
		    }
		    if (! rfeas) {
			continue;
		    }		    
		    // at this point we know the extension is feasible
		    Label<T> *nl = new Label<T>(label, succ, rc_, d_);
		    bool added = Label<T>::update(labels[succ], nl);
		    if (added) label->addsuccessor(nl);
		    if (added && (! inQ[succ]) && succ != 0) {
			Q.push_back(succ);
			inQ[succ] = true;
		    }
		}
		label->setignore();
	    }
	}
	double bestcost = labels[0][0]->cost();
	for (unsigned int i=1; i < labels[0].size(); i++) {
	    if (labels[0][i]->cost() < bestcost) {
		bestcost = labels[0][i]->cost();
	    }
	}
        // free memory
        for (int n=0; n < nnodes_; n++) {
            for (unsigned int i=0; i < labels[n].size(); i++) {
                free(labels[n][i]);
            }
        }
	return bestcost;
    }
};

#endif
