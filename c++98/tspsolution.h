#ifndef TSPSOLUTION_H
#define TSPSOLUTION_H

#include <vector>
#include <memory>

#include "tspdata.h"

template <class T> class TSPSolution {
protected:
    vector<int> nodes_;
    
    bool first_improvement(const TSPData<T> &data) {
	for (unsigned int p1=0; p1 < nodes_.size() - 3; p1++) {
	    for (unsigned int p2=p1+2; p2 < nodes_.size() - 1; p2++) {
		if (data.d(nodes_[p1], nodes_[p1+1]) +
		    data.d(nodes_[p2], nodes_[p2+1]) > 
		    data.d(nodes_[p1], nodes_[p2]) +
		    data.d(nodes_[p1+1], nodes_[p2+1])) {
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
    TSPSolution(const vector<int> &permutation) {
	nodes_ = permutation;
    }
    
    int two_opt(const TSPData<T> &data) {
	int t = 0;
	while (first_improvement(data)) t++;
	return t;
    }
};

#endif
