#ifndef TSPDATA_H
#define TSPDATA_H

#include <vector>
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>

using namespace std;

vector<string> tokenize(string line) {
    vector<string> tokens;
    stringstream tok(line);
    string tmp;
    while (tok >> tmp) tokens.push_back(tmp);
    return tokens;
}

template <class T> class TSPData {
protected:
    // number of points
    unsigned int n_;
    // distance matrix
    T *d_;
    // distance matrix helper
    T **dh_;
    // auxiliary graph for e.g. espprc
    double *aux_;

public:
    TSPData(int n, T *d) {
	n_ = n;
	d_ = d;
	dh_ = new T*[n];
	for (int i=0; i < n; i++)
	    dh_[i] = d_ + n * i;
    }
    // ~TSPData() { delete[] d_; }
    // load data from file
    TSPData(string fname) {
    }
    // getters are here
    const T d(int i, int j) const { return dh_[i][j]; }
    const int n() const { return n_; }
    const T *d() const { return d_; }
    // used to store data for auxiliary graphs, typically needs to be
    // allocated once then overwritten many times
    double *aux() { return aux_; }
};

#endif
