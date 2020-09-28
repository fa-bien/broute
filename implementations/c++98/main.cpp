#include <cstdlib>
#include <iostream>
#include <string>

#include "tspdata.h"
#include "tspsolution.h"

// read input file and return corresponding data and solutions
template<class T> pair<TSPData<T>, vector<TSPSolution<T> > >
read_data(string fname) {
    unsigned int n = 0;
    T *d=NULL;
    unsigned int ditems = 0;
    vector<vector<int> > tours;
    vector<TSPSolution<T> > solutions;
    unsigned int nsols = 0;
    ifstream infile(fname.c_str());
    if (! infile.is_open()) {
	cerr << "Can't open file: " << fname << endl;
	exit(2);
    }
    string line;
    while (! infile.eof()) {
	getline(infile, line);
	// remove comments
	line = line.substr(0, line.find("#"));
	vector<string> tokens = tokenize(line);
	if (tokens.size() == 0) {
	    continue;
	} else if (n == 0 and tokens.size() == 2) {
	    n = atoi(tokens[0].c_str());
	    nsols = atoi(tokens[1].c_str());
	    d = (int*) malloc(n*n*sizeof(T));
	} else if (ditems < n*n) {
	    stringstream gg(line);
	    for (unsigned int i=0; i < n; i++) {
		gg >> d[ditems++];
	    }
	} else if (tours.size() < nsols) {
	    vector<int> tour;
	    int tmp;
	    stringstream gg(line);
	    for (unsigned int i=0; i < n + 1; i++) {
		gg >> tmp;
		tour.push_back(tmp);
	    }
	    tours.push_back(tour);
	}
    }
    TSPData<T> data(n, d);
    
    for (unsigned int i=0; i < tours.size(); i++) {
    	solutions.push_back(TSPSolution<T>(tours[i]));
    }
    return make_pair(data, solutions);
}

// benchmark all solutions in the given vector
template<class T> pair<int, double>
benchmark_one(const TSPData<T> &data, vector<TSPSolution<T> > solutions,
	      string benchmarkname) {
    int nimpr = 0;
    double total_ls = 0;
    int n;
    for (unsigned int i=0; i < solutions.size(); i++) {
	clock_t t2 = clock();
	if (benchmarkname == "2-opt") {
	    n = solutions[i].two_opt(data);
	} else if (benchmarkname == "Or-opt") {
	    n = solutions[i].or_opt(data);
	} else {
	    cerr << "Unknown benchmark: " << benchmarkname << endl;
	    exit(2);
	}
	clock_t t3 = clock();
	total_ls += ((double)(t3-t2)) / CLOCKS_PER_SEC;
	nimpr += n;
    }
    return make_pair(nimpr, total_ls);
}

string basename(string fname) {
    string t = "./" + fname;
    return t.substr(1+t.rfind("/"));
}

int main (int argc, char * argv[]) {
    if (argc < 2) {
	cerr << "USAGE: " << argv[0] << " tsp_data_file [benchmark]" << endl;
	exit(0);
    } else {
	pair<TSPData<int>, vector<TSPSolution<int> > > all_data =
	    read_data<int>(argv[1]);
	string benchmarkname = "2-opt";
	if (argc > 2) {
	    benchmarkname = argv[2];
	}
	TSPData<int> data = all_data.first;
	vector<TSPSolution<int> > solutions = all_data.second;
	pair<int, double> res = benchmark_one<int>(data, solutions,
						   benchmarkname);
	cout << "c++," << COMPILER << " " << __VERSION__ << ","
	     << benchmarkname << ","
	     << basename(argv[1]) << ","
	     << data.n() << ","
	     << solutions.size() << "," << res.first << "," << res.second
	     << endl;
    }
    return 0;
}
