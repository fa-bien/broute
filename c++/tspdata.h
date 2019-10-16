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
    int *d_;

public:
    TSPData(int n, int *d) {n_ = n; d_ = d;}
    // ~TSPData() { delete[] d_; }
    // load data from file
    TSPData(string fname) {
    }
    // getters are here
    T d(int i, int j) const { return d_[i*n_+j]; }
    int n() const { return n_; }
};

#endif
