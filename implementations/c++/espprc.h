#ifndef ESPPRC_H
#define ESPPRC_H

#include <vector>
#include <iostream>
#include <set>
#include <deque>
#include <memory>

using namespace std;

template <class T> class Label {
protected:
    // where we're at
    int at_;
    // already visited nodes
    set<int> visited_;
    // has this label already been extended?
    bool ignore_;
    // predecessor label
    shared_ptr<Label> pred_;
    //
    double cost_;
    T length_;
    // resource consumption
    vector<int> q_;
    // successors for later recursive deletion when dominated
    vector<shared_ptr<Label>> successors_;

    // number of resources considered
    static int nresources;

    // number of vertices (also gives dimension of cost/len matrix)
    static int nnodes;
    
public:
    Label() {
        at_ = 0;
	visited_ = set<int>();
        ignore_ = false;
	pred_ = make_shared(*this);
        cost_ = 0.0;
        length_ = 0;
	q_ = vector<int>(nresources, 0);
	successors_ = vector<shared_ptr<Label>>();
    }

    bool dominates(const Label &other) {
	if (cost_ > other.cost_ || length_ > other.length_) return false;
	for(auto v: visited_) {
	    if (other.visited_.find(v) == other.visited_.end()) return false;
	}
	for (unsigned int i=0; i < nresources; i++) {
	    if (q_[i] > other.q_[i]) return false;
	}
	return true;
    }

    Label extend(int vertex, int *rc, int *d) {
	Label nl();
	nl.at = vertex;
	nl.pred = make_shared(*this);
	nl.visited_ = visited_;
	nl.visited_.insert(vertex);
	nl.cost_ = cost_ + rc[at_ * nnodes + vertex];
	nl.length_ = length_ + d[at_ * nnodes + vertex];
	nl.q_ = q_;
	for (unsigned int r=0; r < nresources; r++) {
	    if (vertex & (1 << r) > 0) q_[r] += 1;
	}
	successors_.push_back(make_shared(*this));
	return nl;
    }

    void markSuccessors() {
	for (auto s: successors_) {
	    s->ignore_ = true;
	    s-> markSuccessors();
	}
    }

};


template <class T> class ESPPRC {
protected:
    int nnodes_;
    // reduced cost flat matrix
    int *rc_;
    // length flat matrix
    T *d_;
    // number of resources considered for resource constraints
    int nresources_;
    // capacity for each resource
    int resourcecapacity_;
    
public:
    ESPPRC(int nnodes, int *rc, int *d, int nresources, int resourcecapacity) {
	nnodes_ = nnodes;
	rc_ = rc;
	d_ = d;
	nresources_ = nresources;
	resourcecapacity_ = resourcecapacity;
    }

    int solve(int maxlen){
	Label<T>::nresources = nresources_;
	Label<T>::nnodes = nnodes_;
	Label<T> l();
	//
	return 0;
    }
};

#endif
