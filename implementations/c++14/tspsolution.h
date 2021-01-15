#ifndef TSPSOLUTION_H
#define TSPSOLUTION_H

#include <vector>
#include <memory>
#include <climits>

#include "tspdata.h"
#include "espprc.h"
#include "espprc-index.h"
#include "maxflow.h"

template <class T> class TSPSolution {
protected:
    shared_ptr<TSPData<T> > data_;
    vector<int> nodes_;
    
    bool first2eimprovement() {
	for (unsigned int p1=0; p1 < nodes_.size() - 3; p1++) {
	    for (unsigned int p2=p1+2; p2 < nodes_.size() - 1; p2++) {
		if (data_->d(nodes_[p1], nodes_[p1+1]) +
		    data_->d(nodes_[p2], nodes_[p2+1]) > 
		    data_->d(nodes_[p1], nodes_[p2]) +
		    data_->d(nodes_[p1+1], nodes_[p2+1])) {
		    int t;
		    for (unsigned int i=0; i < ((p2-p1+1) / 2); i++) {
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

    // used in Or-opt
    inline int or_delta(unsigned int i, unsigned int l, unsigned int p) {
	return data_->d(nodes_[i-1], nodes_[i+l])
	    + data_->d(nodes_[p], nodes_[i])
	    + data_->d(nodes_[i+l-1], nodes_[p+1])
	    - data_->d(nodes_[p], nodes_[p+1])
	    - data_->d(nodes_[i-1], nodes_[i])
	    - data_->d(nodes_[i+l-1], nodes_[i+l]);
    }
    
    bool firstorimprovement() {
	for (unsigned int i=1; i < nodes_.size() - 1; i++) {
	    for (unsigned int l=1;
		 l < 1 + min((long unsigned)3, nodes_.size() - 1 - i); l++) {
		for (unsigned int p=0; p < i-1; p++) {
		    int delta = or_delta(i, l, p);
		    if (delta < 0) {
			// first copy sequence we want to move
			int *t = new int[l];
			for(unsigned int j=0; j < l; j++) {
			    t[j] = nodes_[i+j]; }
			// next move around what will end up being right of it
			for(unsigned int j=i-1; j > p; j--) {
			    nodes_[j+l] = nodes_[j]; }
			// finally write in the sequence being moved
			for(unsigned int j=0; j < l; j++) {
			    nodes_[p+1+j] = t[j]; }
			return true;
		    }
		}
		for (unsigned int p=i+l; p < nodes_.size() - 1; p++) {
		    int delta = or_delta(i, l, p);
		    if (delta < 0) {
			// first copy sequence we want to move
			int *t = new int[l];
			for(unsigned int j=0; j < l; j++) {
			    t[j] = nodes_[i+j]; }
			// next move around what will end up being left of it
			for(unsigned int j=i+l; j <= p; j++) {
			    nodes_[j-l] = nodes_[j]; }
			// finally write in the sequence being moved
			for (unsigned int j=0; j < l; j++) {
			    nodes_[p+1+j-l] = t[j]; }
			return true;
		    }
		}
	    }
	}
	return false;
    }

public:
    TSPSolution(shared_ptr<TSPData<T> > data, const vector<int> &permutation) {
	data_ = data;
	nodes_ = permutation;
    }
    
    int two_opt() {
	int t = 0;
	while (first2eimprovement()) t++;
	return t;
    }

    int or_opt() {
	int t = 0;
	while (firstorimprovement()) t++;
	return t;
    }

    int lns(unsigned int niter=10) {
	T checksum = 0;
	for (unsigned int iter=0; iter < niter; iter++) {
	    // step 0: copy solution
	    vector<int> tmp = nodes_;
	    vector<int> unplanned;
	    // step 1: destroy
	    unsigned int where = 1;
	    while (where < tmp.size() - 1) {
		unplanned.push_back(tmp[where]);
		tmp.erase(tmp.begin() + where);
		where += 1;
	    }
	    // step 2: repair
	    while (unplanned.size() > 0) {
		unsigned int bestfrom=0, bestto=0;
		// should be big enough and castable for any relevant type
		T bestcost = INT_MAX;
		for (unsigned int k=0; k < unplanned.size(); k++) {
		    for (unsigned to=0; to < tmp.size() -1; to++) {
			T delta = data_->d(tmp[to], unplanned[k]) +
			    data_->d(unplanned[k], tmp[to+1]) -
			    data_->d(tmp[to], tmp[to+1]);
			if (delta < bestcost) {
			    bestcost = delta;
			    bestfrom = k;
			    bestto = to;
			}
		    }
		}
		// perform best found insertion
		tmp.insert(tmp.begin() + bestto + 1, unplanned[bestfrom]);
		unplanned.erase(unplanned.begin() + bestfrom);
		checksum += bestcost;
	    }
	    // step 3: move or not
	    nodes_ = tmp;
	}
	return (int) checksum;
    }

    int espprc(int nresources=6, int resourcecapacity=1, bool index=false) {
	int n = data_->n();
	const T *d = data_->d();
	// reduced cost graph calculation
	double *rc = data_->aux();
	vector<double> dual(n, 0.0);
	for (unsigned int t=0; t < nodes_.size() - 1; t++) {
	    int i = nodes_[t];
	    int j = nodes_[t+1];
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
	    int best = INT_MAX;
	    for (int j=0; j < n; j++) {
		if (i == j) continue;
		if (d[i*n+j] < best) {
		    best = d[i*n+j];
		}
	    }
	    bestassignment += best;
	}
	int maxlen = bestassignment;
        if (! index) {
            ESPPRC<T> e(n, rc, d, nresources, resourcecapacity, maxlen);
            return (int) e.solve();
        } else {
            ESPPRCLC<T> e(n, rc, d, nresources, resourcecapacity, maxlen);
            return (int) e.solve();
        }
    }

    int maxflow() {
	int n = data_->n();
	const T *d = data_->d();
	// capacity graph
	double *C = data_->aux();
        // flow graph
        double *F = data_->aux2();
	vector<double> t(n, 0.0);
	for (unsigned int k=0; k < nodes_.size() - 1; k++) {
	    int i = nodes_[k];
	    int j = nodes_[k+1];
	    t[j] = (double) d[i*n+j];
	}
	for (int i=0; i < n; i++) {
	    for (int j=0; j < n; j++) {
		C[i*n+j] = d[i*n+j] > t[j] ? d[i*n+j] / 1000.0 : 0.0;
	    }
	}
        // solve maxflow for each non-0 node as sink
        double checksum = 0.0;
        for (int sink=1; sink < n; sink++) {
            double mf = edmondskarp(C, F, n, 0, sink);
            checksum += mf;
        }
        return (int) checksum;
    }
    
    const shared_ptr<TSPData<T> > data(){ return data_; }
};

#endif
