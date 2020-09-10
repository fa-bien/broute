#ifndef TSPSOLUTION_H
#define TSPSOLUTION_H

#include <vector>
#include <memory>
#include <cstdio>
#include <cstring>

#include "tspdata.h"

template <class T> class TSPSolution {
protected:
    shared_ptr<TSPData<T> > data_;
    int *nodes_;
    int size_;
    
    bool first2eimprovement() {
	for (int p1=0; p1 < size_ - 3; p1++) {
	    for (int p2=p1+2; p2 < size_ - 1; p2++) {
		if (data_->d(nodes_[p1], nodes_[p1+1]) +
		    data_->d(nodes_[p2], nodes_[p2+1]) > 
		    data_->d(nodes_[p1], nodes_[p2]) +
		    data_->d(nodes_[p1+1], nodes_[p2+1])) {
		    int t;
		    for (int i=0; i < ((p2-p1+1) / 2); i++) {
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
	for (int i=1; i < size_ - 1; i++) {
	    for (int l=1; l < 1 + min(3, size_ - 1 - i); l++) {
		for (int p=0; p < i-1; p++) {
		    int delta = or_delta(i, l, p);
		    if (delta < 0) {
			// first copy sequence we want to move
			int *t = new int[l];
			memcpy(t, nodes_ + i, l * sizeof(int));
			// next move around what will end up being right of it
			memmove(nodes_ + p + l + 1,
				nodes_ + p + 1,
				(i - p - 1)* sizeof(int));
			// finally write in the sequence being moved
			memcpy(nodes_ + p + 1, t, l * sizeof(int));
			return true;
		    }
		}
		for (int p=i+l; p < size_ - 1; p++) {
		    int delta = or_delta(i, l, p);
		    if (delta < 0) {
			// first copy sequence we want to move
			int *t = new int[l];
			memcpy(t, nodes_ + i, l * sizeof(int));
			// next move around what will end up being left of it
			memmove(nodes_ + i, nodes_ + i + l,
				(p + 1 - (i + l)) * sizeof(int));
			// finally write in the sequence being moved
			memcpy(nodes_ + p + 1 - l, t, l * sizeof(int)); 
			return true;
		    }
		}
	    }
	}
	return false;
    }
    
public:
    TSPSolution(shared_ptr<TSPData<T> > data, int *permutation) {
	data_ = data;
	size_ = data_->n() + 1;
	nodes_ = new int[size_];
	memcpy(nodes_, permutation, size_ * sizeof(int));
    }

    // ~TSPSolution() { delete[] nodes_; }
    
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
