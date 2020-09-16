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
	while(this.first2eImprovement()) {
	    t += 1;
	}
	return t;
    }

    // perform the first improving two-exchange found
    var tour = this.nodes;
    var d = this.data.d;
    this.first2eImprovement = function() {
	for(var p1=0; p1 < tour.length - 3; p1++) {
	    for(var p2=p1+2; p2 < tour.length - 1; p2++) {
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

    // perform first-improvement 2-opt
    this.orOpt = function() {
	var t = 0;
	while(this.firstOrImprovement()) {
	    t += 1;
	}
	return t;
    }

    this.orDelta = function(i, l, p) {
	return d[tour[i-1]][tour[i+l]] + d[tour[p]][tour[i]]
	    + d[tour[i+l-1]][tour[p+1]] - d[tour[p]][tour[p+1]]
	    - d[tour[i-1]][tour[i]] - d[tour[i+l-1]][tour[i+l]];
    }
	
    // perform the first improving Or move found
    this.firstOrImprovement = function() {
	for(var i=1; i < tour.length - 1; i++) {
	    for(var l=1; l < 1 + Math.min(3, tour.length - 1 - i); l++) {
		for(var p=0; p < i-1; p++) {
		    if (this.orDelta(i,l,p) < 0) {
			let t = tour.splice(i, l);
			tour.splice(p+1, 0, ...t);
			return true;
		    }
		}
		for(var p=i+l; p < tour.length - 1; p++) {
		    if (this.orDelta(i,l,p) < 0) {
			let t = tour.splice(i, l);
			tour.splice(p+1-l, 0, ...t);
			return true;
		    }
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

function benchmarkOne(path, benchmarkname) {
    var [data, solutions] = readData(path);
    var fname = path.split('/').pop();;
    var nimpr = 0;
    var n = 0;
    var totalTime = 0.0;
    var t1=0.0, t2=0.0;
    for(s in solutions){
	var sol = solutions[s];
	t1 = process.hrtime();
	if (benchmarkname == '2-opt') {
	    n = sol.twoOpt();
	} else if (benchmarkname == 'Or-opt') {
	    n = sol.orOpt();
	} else {
	    console.log('Unknown benchmark: ', benchmarkname);
	}
	t2 = process.hrtime(t1);
	totalTime += t2[1] / 1e9;
	nimpr += n;
    }
    console.log(['javascript', benchmarkname, fname,
		 data.n, solutions.length, nimpr, totalTime].join());
}

function main(args) {
    if (args.length < 3) {
	console.log('USAGE:', args[1], 'tsp_instance_file');
    } else {
	benchmarkname = '2-opt';
	if (args.length > 3) benchmarkname = args[3];
	benchmarkOne(args[2], benchmarkname);
    }
}

main(process.argv);
