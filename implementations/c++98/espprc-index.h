#ifndef ESPPRC_INDEX_H
#define ESPPRC_INDEX_H

#include <vector>
#include <iostream>
#include <set>
#include <deque>
#include <memory>
#include<cstring>

using namespace std;

template <class T> class LabelWithIndex {
protected:
    // where we're at
    int at_;
    // already visited nodes
    bool *visited_;
    // has this label already been extended?
    bool ignore_;
    // index of predecessor label in collection
    int pred_;
    //
    double cost_;
    T length_;
    // resource consumption
    int *q_;
    // successors for later recursive deletion when dominated
    vector<int> successors_;

public:

    // number of resources considered
    static int nresources;

    // number of vertices (also gives dimension of cost/len matrix)
    static int nnodes;

    // create an initial dummy label
    LabelWithIndex() {
        at_ = 0;
	visited_ = new bool[nnodes]();
        ignore_ = false;
	pred_ = -1;
        cost_ = 0.0;
        length_ = 0;
	q_ = new int[nresources]();
	successors_ = vector<int>(0);
    }

    // constructor by extension
    LabelWithIndex(double *rc, const T *d,
                   const LabelWithIndex<T> &pred, const int predindex,
                   const int to) {
	ignore_ = false;
	at_ = to;
	pred_ = predindex;
	visited_ = new bool[nnodes];
        memcpy(visited_, pred.visited_, nnodes * sizeof(bool));
	visited_[to] = true;
	cost_ = pred.cost_ + rc[pred.at_ * nnodes + to];
	length_ = pred.length_ + d[pred.at_ * nnodes + to];
	q_ = new int[nresources];
        memcpy(q_, pred.q_, nresources * sizeof(int));
	for (int r=0; r < nresources; r++) {
	    if ((to & (1 << r)) > 0) {
		q_[r] += 1;
	    }
	}
    }

    const bool dominates (const LabelWithIndex<T> &other) const {
	if (cost_ > other.cost_ || length_ > other.length_) return false;
	for(int i=0; i < nnodes; i++) {
	    if (visited_[i] && ! other.visited_[i]) return false;
	}
	for (int i=0; i < nresources; i++) {
	    if (q_[i] > other.q_[i]) return false;
	}
	return true;
    }

    void addsuccessor(int successor) {
	successors_.push_back(successor);
    }

    bool ignore() const { return ignore_; }
    void setignore() { ignore_ = true; }

    bool visits(int n) const { return visited_[n]; }

    T length() const { return length_; }
    double cost() const { return cost_; }
    int at() const { return at_; }

    int getrusage(int r) const { return q_[r]; }

    vector<int> successors() const { return successors_; }

    vector<int>::iterator succbegin() { return successors_.begin(); }
    vector<int>::iterator succend() { return successors_.end(); }
    
};

template<class T>
ostream& operator<<(ostream &os, const LabelWithIndex<T> &l) {
    os << "Label at node " << l.at() << "\tcost = " << l.cost()
       << "\tlength = " << l.length() << "\trusage:";
    for (int i=0; i < Label<T>::nresources; i++) {
	os << " " << l.getrusage(i);
    }
    os << "\tvisited:";
    for (int i=0; i < LabelWithIndex<T>::nnodes; i++) {
	if (l.visits(i)) { cout << " " << i; }
    }
    os << "\tignore = " << l.ignore()
       << "\t successors: " << l.successors().size();
    return os;
}

// it's 2021, C++ still requires global definition of class variables
// this is why we can't have nice things
template<class T> int LabelWithIndex<T>::nresources = 0;
template<class T> int LabelWithIndex<T>::nnodes = 0;

template <class T> class LabelCollection {
private:
    vector<LabelWithIndex<T> > labels_;

public:
    LabelCollection() {}
    
    int emptylabel() {
        labels_.push_back(LabelWithIndex<T>());
        return labels_.size() - 1;
    }

    int extend(double *rc, const T *d, int from, int to) {
        LabelWithIndex<T> nl(rc, d, labels_[from], from, to);
        labels_.push_back( nl );
        return labels_.size() - 1;
    }
    
    void addsuccessor(int from, int to) {
        labels_[from].addsuccessor(to);
    }

    void marksuccessors(int index) {
        for (vector<int>::iterator it = labels_[index].succbegin();
             it != labels_[index].succend();
             it++) {
            labels_[*it].setignore();
            marksuccessors(*it);
        }
    }

    bool updatedominance(vector<int> &labels, int nlindex) {
        unsigned int i = 0;
        while (i < labels.size()) {
            if (labels_[labels[i]].dominates(labels_[nlindex])) {
                return false;
            }
            if (labels_[nlindex].dominates(labels_[labels[i]])) {
                marksuccessors(labels[i]);
                if (i < labels.size() - 1) {
                    labels[i] = labels.back();
                }
                labels.pop_back();
            } else {
                i += 1;
            }
        }
        // at this point the new label is added
        labels.push_back(nlindex);
        return true;
    }

    bool ignore(int lindex) const { return labels_[lindex].ignore(); }
    void setignore(int lindex) { labels_[lindex].setignore(); }
    
    bool visits(int lindex, int node) const {
        return labels_[lindex].visits(node); }

    T length(int lindex) const { return labels_[lindex].length(); }
    double cost(int lindex) const { return labels_[lindex].cost(); }

    int getrusage(int lindex, int r) const {
        return labels_[lindex].getrusage(r); }
};

template <class T> class ESPPRCLC {
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
    ESPPRCLC(int nnodes, double *rc, const T *d,
	   int nresources, int rescap, T maxlen) {
	nnodes_ = nnodes;
	d_ = d;
	rc_ = rc;
	nresources_ = nresources;
	resourcecapacity_ = rescap;
	maxlen_ = maxlen;
    }

    int solve(){
	// set class variables
	LabelWithIndex<T>::nresources = nresources_;
	LabelWithIndex<T>::nnodes = nnodes_;
	// initial label (empty path) and queue
        LabelCollection<T> lc;
        int l = lc.emptylabel();
	deque<int> Q;
        bool *inQ = new bool[nnodes_]();
	Q.push_back(0);
	inQ[0] = true;
	vector<int> *labels = new vector<int>[nnodes_]();
	labels[0].push_back(l);
	// main DP loop
	while (! Q.empty()) {
	    int n = Q.front();
	    Q.pop_front();
	    inQ[n] = false;
	    for (unsigned int i=0; i < labels[n].size(); i++) {
                int lind = labels[n][i];
		if (lc.ignore(lind)) {
		    continue;
		}
		for (int succ = 0; succ < nnodes_; succ++) {
		    if (lc.visits(lind, succ) || succ == n) {
			continue;
		    }
                    // succ is a candidate for extension; is it length-feasible?
                    if (lc.length(lind)
			+ d_[n*nnodes_+succ] + d_[succ*nnodes_] > maxlen_) {
			continue;
		    }
		    // is it resource-feasible ?
		    bool rfeas = true;
		    for (int i=0; i < nresources_; i++) {
			if ( (succ & (1 << i)) > 0 &&
			     lc.getrusage(lind, i) + 1 > resourcecapacity_ ) {
			    rfeas = false;
			    break;
			}
		    }
		    if (! rfeas) {
			continue;
		    }		    
		    // at this point we know the extension is feasible
		    int nl = lc.extend(rc_, d_, lind, succ);
		    bool added = lc.updatedominance(labels[succ], nl);
		    if (added) lc.addsuccessor(lind, nl);
		    if (added && (! inQ[succ]) && succ != 0) {
			Q.push_back(succ);
			inQ[succ] = true;
		    }
		}
		lc.setignore(lind);
	    }
	}
	double bestcost = lc.cost(labels[0][0]);
	for (unsigned int i=1; i < labels[0].size(); i++) {
	    if (lc.cost(labels[0][i]) < bestcost) {
		bestcost = lc.cost(labels[0][i]);
	    }
	}
	return (int) bestcost;
    }
};

#endif
