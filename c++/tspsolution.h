#ifndef TSPSOLUTION_H
#define TSPSOLUTION_H

#include <vector>
#include <memory>

#include "tspdata.h"

template <class T> class TSPSolution {
protected:
    shared_ptr<TSPData<T> > data_;
    vector<int> nodes_;
    
    bool first_improvement() {
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
    
public:
    TSPSolution(shared_ptr<TSPData<T> > data, const vector<int> &permutation) {
	data_ = data;
	nodes_ = permutation;
    }
    
    int two_opt() {
	int t = 0;
	while (first_improvement()) t++;
	return t;
    }

    const shared_ptr<TSPData<T> > data(){ return data_; }
};

#endif
