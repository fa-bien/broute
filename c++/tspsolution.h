#ifndef TSPSOLUTION_H
#define TSPSOLUTION_H

#include <vector>
#include <memory>

#include "tspdata.h"

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
			for(unsigned int j=0; j < l; j++) { t[j] = nodes_[i+j]; }
			// next move around what will end up being right of it
			for(unsigned int j=i-1; j > p; j--) { nodes_[j+l] = nodes_[j]; }
			// finally write in the sequence being moved
			for(unsigned int j=0; j < l; j++) { nodes_[p+1+j] = t[j]; }
			
			return true;
		    }
		}
		for (unsigned int p=i+l; p < nodes_.size() - 1; p++) {
		    int delta = or_delta(i, l, p);
		    if (delta < 0) {

			// first copy sequence we want to move
			int *t = new int[l];
			for(unsigned int j=0; j < l; j++) { t[j] = nodes_[i+j]; }
			// next move around what will end up being left of it
			for(unsigned int j=i+l; j <= p; j++) { nodes_[j-l] = nodes_[j]; }
			// finally write in the sequence being moved
			for (unsigned int j=0; j < l; j++) { nodes_[p+1+j-l] = t[j]; }
			
			
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

    const shared_ptr<TSPData<T> > data(){ return data_; }
};

#endif
