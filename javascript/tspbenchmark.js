#!/usr/bin/env node

// class: TSP instance
function TSPData(n, d) {
    this.n = n;
    this.d = d;
}

// class: TSP Solution
function TSPSolution(data, sequence) {
    this.data = data;
    this.nodes = sequence;

    // perform first-improvement 2-opt
    this.twoOpt = function() {
	var t = 0;
	while(this.firstImprovement()) {
	    t += 1;
	}
	return t;
    }

    // perform the first improvement found
    var tour = this.nodes;
    var d = this.data.d;
    this.firstImprovement = function() {
	for(var p1=0; p1 < this.nodes.length - 3; p1++) {
	    for(var p2=p1+2; p2 < this.nodes.length - 1; p2++) {
		if (d[tour[p1]][tour[p1+1]] + d[tour[p2]][tour[p2+1]] >
		    d[tour[p1]][tour[p2]] + d[tour[p1+1]][tour[p2+1]]) {
		    // improving 2-exchange found
		    for(var i=0; i < Math.floor((p2-p1+1) / 2); i++) {
			[tour[p1+1+i], tour[p2-i]] = [tour[p2-i], tour[p1+1+i]];
		    }
		    return true;
		}
	    }
	}
	return false;
    };    
}

// this version requires node
function fileAsLines(fname) {
    var fs = require('fs');
    return fs.readFileSync(fname).toString().split("\n");
}

function readData(fname) {
    var n = 0;
    var d = [];
    var tours = [];
    var nsols = 0;
    fileAsLines(fname).forEach(line => {
	var tokens = line.replace(/#.*/i, '').split(' ');
	if (tokens.length == 0) {
	    ;
	} else if (n == 0 && tokens.length == 2) {
	    n = parseInt(tokens[0]);
	    nsols = parseInt(tokens[1]);
	} else if (tokens.length == n && d.length < n) {
	    d.push(tokens.map(x => parseInt(x)));
	} else if (tokens.length == n+1 && tours.length < nsols) {
	    tours.push(tokens.map(x => parseInt(x)));
	}
    });
    var data = new TSPData(n, d);
    var sols = tours.map(x => new TSPSolution(data, x));
    return [data, sols];
}

function benchmarkOne(solutions) {
    var nimpr = 0;
    var n = 0;
    var total2optTime = 0.0;
    var t1=0.0, t2=0.0;
    solutions.forEach(sol => {
	t1 = process.hrtime();
	n = sol.twoOpt();
	t2 = process.hrtime(t1);
	total2optTime += t2[1] / 1e9;
	nimpr += n;
    });
    return [nimpr, total2optTime];
}

function benchmarkMany(dirname, benchmarkname) {
    var fs = require('fs');
    fs.readdir(dirname, (err, entries) => {
	entries.forEach(fname => {
	    var path = [dirname, fname].join('/');
	    var [data, solutions] = readData(path);
	    var res = benchmarkOne(solutions);
	    console.log(['javascript', benchmarkname, fname,
			 data.n, solutions.length,
			 res[0], res[1]].join());
	});
    });
}

function main(args) {
    if (args.length != 3) {
	console.log('USAGE:', args[1], 'tsp_data_file_dir');
    } else {
	benchmarkMany(args[2], '2-opt');
    }
}

main(process.argv);
