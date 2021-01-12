#!/usr/bin/env node

// class: TSP instance
function TSPData(n, d) {
    this.n = n;
    this.dist = d;
    this.aux = new Array(d.length);
    this.aux2 = new Array(d.length);

    this.d = function(i, j) {
	return this.dist[i * this.n + j];
    }
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
    var d = this.data;
    this.first2eImprovement = function() {
	for(var p1=0; p1 < tour.length - 3; p1++) {
	    for(var p2=p1+2; p2 < tour.length - 1; p2++) {
		if (d.d(tour[p1], tour[p1+1]) + d.d(tour[p2], tour[p2+1]) >
		    d.d(tour[p1], tour[p2]) + d.d(tour[p1+1], tour[p2+1])) {
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
	return d.d(tour[i-1], tour[i+l]) + d.d(tour[p], tour[i])
	    + d.d(tour[i+l-1], tour[p+1]) - d.d(tour[p], tour[p+1])
	    - d.d(tour[i-1], tour[i]) - d.d(tour[i+l-1], tour[i+l]);
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

    // lns!
    this.lns = function(niter=10) {
	var checksum = 0;
	for (var iter=0; iter < niter; iter++) {
	    // step 0: copy solution
	    var tmp = [...tour];
	    var unplanned = [];
	    // step 1: destroy
	    var where = 1;
	    while (where < tmp.length - 1) {
		unplanned.push(tmp[where]);
		tmp.splice(where, 1);
		where += 1;
	    }
	    // step 2: repair
	    while (unplanned.length > 0) {
		var bestfrom=0, bestto=0, bestcost = Number.MAX_SAFE_INTEGER;
		for (var k=0; k < unplanned.length; k++) {
		    for (var to=0; to < tmp.length - 1; to++) {
			var delta = d.d(tmp[to], unplanned[k]) +
			    d.d(unplanned[k], tmp[to+1]) -
			    d.d(tmp[to], tmp[to+1]);
			if (delta < bestcost) {
			    bestcost = delta;
			    bestfrom = k;
			    bestto = to;
			}
		    }
		}
		// perform best found insertion
		tmp.splice(bestto + 1, 0, unplanned[bestfrom]);
		unplanned.splice(bestfrom, 1);
		checksum += bestcost;
	    }
	    // step 3: move or not
	    tour = tmp;
	}
	return checksum;
    }

    // ESPPRC
    this.espprc = function(nresources=6, resourcecapacity=1, index=false) {
        var dual = new Array(data.n);
        var rc = data.aux;
        var n = data.n;
        for (var t=0; t < tour.length -1; t++) {
            var i = tour[t];
            var j = tour[t+1];
            dual[j] = 1.0 * d.d(i, j);
        }
        for (var i=0; i < data.n; i++) {
            for (var j=0; j < data.n; j++) {
                rc[i*n+j] = d.dist[i*n+j] - dual[j];
            }
        }
        var bestassignment = 0;
        for (var i=0; i < n; i++) {
            var best = Number.MAX_SAFE_INTEGER;
            for (var j=0; j < n; j++) {
                if (i == j) continue;
                if (d.d(i, j) < best) {
                    best = d.d(i, j);
                }
            }
            bestassignment += best;
        }
        var maxlen = bestassignment;
        if (! index) {
            var e =
                new ESPPRC(n, rc, d.dist, nresources, resourcecapacity, maxlen);
        } else {
            var e = new ESPPRCLC(n, rc, d.dist,
                                 nresources, resourcecapacity, maxlen);
        }
        return Math.round(e.solve());
    }

    // max flow
    this.maxflow = function() {
        var C = d.aux;
        var F = d.aux2;
        var n = d.n;
        var t = new Array(n);
        for (var k=0; k < tour.length - 1; k++) {
            var i = tour[k];
            var j = tour[k+1];
            t[j] = d.d(i, j);
        }
        for (var i=0; i < data.n; i++) {
            for (var j=0; j < data.n; j++) {
                C[i*n+j] = d.d(i, j) > t[j] ? 1.0 * d.d(i, j) : 0.0;
            }
        }
        var checksum = 0.0;
        for (var sink=1; sink < d.n; sink++) {
            var mf = edmondskarp(C, F, n, 0, sink);
            checksum += mf;
        }
        return Math.round(checksum);
    }
}

function ESPPRC(n, rc, d, nresources, resourcecapacity, maxlen) {
    this.n = n;
    this.rc = rc;
    this.d = d;
    this.nresources = nresources;
    this.resourcecapacity = resourcecapacity;
    this.maxlen = maxlen;
    
    this.solve = function() {
        var Q = new Array();
        var inQ = new Array(n);
        for (var i=0; i < n; i++) {
            inQ[i] = false;
        }
        labels = new Array(n);
        for (var i=0; i < n; i++) {
            labels[i] = new Array();
        }
        Q.push(0)
        inQ[0] = true;
        labels[0].push(emptyLabel());
        while (Q.length > 0) {
            var t = Q.shift();
            inQ[t] = false;
            for (label of labels[t]) {
                if (label.ignore) continue;
                for (var succ=0; succ < n; succ++) {
                    if (label.visits[succ] || succ == t) continue;
                    // succ is a candidate for extension; is it length-feasible?
                    if (label.length + d[t*n+succ] + d[succ*n] >
                        maxlen)
                        continue;
                    // is it resource-feasible?
                    var rfeas = true;
                    for (var r=0; r < this.nresources; r++) {
                        if ( (succ & (1 << r)) > 0 &&
                             label.q[r] + 1 > resourcecapacity ) {
                            rfeas = false;
                            break;
                        }
                    }
                    if (! rfeas) continue;
                    // at this point we know the extension is feasible
                    nl = label.extend(succ);
                    var added = update(labels[succ], nl);
                    if (added) label.addsuccessor(nl);
                    if ( added && ( ! inQ[succ] && succ != 0 ) ) {
                        Q.push(succ);
                        inQ[succ] = true;
                    }
                }
                label.ignore=true;
            }
        }
        var bestcost = labels[0][0].cost;
        for (var i=1; i < labels[0].length; i++) {
            if (labels[0][i].cost < bestcost) {
                bestcost = labels[0][i].cost;
            }
        }
        return bestcost;
    }

    function Label(at, visits, pred, cost, length, q) {
        this.at = at;
        this.visits = visits;
        this.pred = pred;
        this.cost = cost;
        this.length = length;
        this.q = q;
        this.ignore = false;
        this.successors = new Array();

        this.dominates = function(other) {
            if (this.cost > other.cost || this.length > other.length)
                return false;
            for (var i=0; i < n; i++) {
                if (this.visits[i] && ! other.visits[i]) return false;
            }
            for (var r=0; r < nresources; r++) {
                if (this.q[r] > other.q[r]) return false;
            }
            return true;
        }

        this.extend = function(to) {
            var visits = this.visits.slice();
            visits[to] = true;
            var q = this.q.slice();
	    for (var r=0; r < nresources; r++) {
	        if ((to & (1 << r)) > 0) {
		    q[r] += 1;
	        }
	    }
            var nl = new Label(to,
                               visits,
                               this,
                               this.cost + rc[this.at*n+to],
                               this.length + d[this.at*n+to],
                               q);
            return nl;
        }
        
        this.addsuccessor = function(successor) {
            this.successors.push(successor);
        }

        this.marksuccessors = function() {
            for (succ of this.successors) {
                succ.ignore = true;
                succ.marksuccessors();
            }
        }
    }
    
    function emptyLabel() {
        var visits = new Array(n);
        for (var i=0; i < n; i++) visits[i] = false;
        var q = new Array(nresources);
        for (var r=0; r < nresources; r++) q[r] = 0;
        return new Label(0, visits, null, 0, 0, q);
    }

    // update labels with newlabel, i.e. remove dominated elements as needed.
    // return true if newlabel is added, false otherwise
    function update(labels, newlabel) {
	var i=0;
	while (i < labels.length) {
	    if (labels[i].dominates(newlabel)) {
		return false;
	    }
	    if (newlabel.dominates(labels[i])) {
		labels[i].marksuccessors();
		if (i < labels.length - 1) {
		    labels[i] = labels[labels.length-1];
		}
		labels.pop();
	    } else {
		i += 1;
	    }
	}
	// at this point newlabel is not dominated so we add it
	labels.push(newlabel);
	return true;
    }
}

function ESPPRCLC(n, rc, d, nresources, resourcecapacity, maxlen) {
    this.n = n;
    this.rc = rc;
    this.d = d;
    this.nresources = nresources;
    this.resourcecapacity = resourcecapacity;
    this.maxlen = maxlen;
    
    this.solve = function() {
        var Q = new Array();
        var inQ = new Array(n);
        for (var i=0; i < n; i++) {
            inQ[i] = false;
        }
        labels = new Array(n);
        for (var i=0; i < n; i++) {
            labels[i] = new Array();
        }
        Q.push(0)
        inQ[0] = true;
        var lc = new LabelCollection();
        labels[0].push(lc.emptyLabel());
        while (Q.length > 0) {
            var t = Q.shift();
            inQ[t] = false;
            for (lindex of labels[t]) {
                var label = lc.labels[lindex];
                if (label.ignore) continue;
                for (var succ=0; succ < n; succ++) {
                    if (label.visits[succ] || succ == t) continue;
                    // succ is a candidate for extension; is it length-feasible?
                    if (label.length + d[t*n+succ] + d[succ*n] >
                        maxlen)
                        continue;
                    // is it resource-feasible?
                    var rfeas = true;
                    for (var r=0; r < this.nresources; r++) {
                        if ( (succ & (1 << r)) > 0 &&
                             label.q[r] + 1 > resourcecapacity ) {
                            rfeas = false;
                            break;
                        }
                    }
                    if (! rfeas) continue;
                    // at this point we know the extension is feasible
                    nl = lc.extend(lindex, succ);
                    var added = lc.update(labels[succ], nl);
                    if (added) lc.addsuccessor(lindex, nl);
                    if ( added && ( ! inQ[succ] && succ != 0 ) ) {
                        Q.push(succ);
                        inQ[succ] = true;
                    }
                }
                label.ignore=true;
            }
        }
        var bestcost = lc.labels[labels[0][0]].cost;
        for (var i=1; i < labels[0].length; i++) {
            if (lc.labels[labels[0][i]].cost < bestcost) {
                bestcost = lc.labels[labels[0][i]].cost;
            }
        }
        return bestcost;
    }

    function LabelCollection() {
        this.labels = new Array();

        this.emptyLabel = function() {
            var visits = new Array(n);
            for (var i=0; i < n; i++) visits[i] = false;
            var q = new Array(nresources);
            for (var r=0; r < nresources; r++) q[r] = 0;
            this.labels.push(new Label(0, visits, -1, 0, 0, q));
            return this.labels.length - 1;
        }

        this.extend = function(fromindex, to) {
            this.labels.push(this.labels[fromindex].extend(fromindex, to));
            return this.labels.length - 1;
        }

        this.addsuccessor = function(lindex, successor) {
            this.labels[lindex].successors.push(successor);
        }

        this.marksuccessors = function(lindex) {
            for (succ of this.labels[lindex].successors) {
                this.labels[succ].ignore = true;
                this.marksuccessors(succ);
            }
        }
        
        // update labels with newlabel, removing dominated elements as needed.
        // return true if newlabel is added, false otherwise
        this.update = function (labels, newlabel) {
	    var i=0;
	    while (i < labels.length) {
	        if (this.labels[labels[i]].dominates(this.labels[newlabel])) {
		    return false;
	        }
	        if (this.labels[newlabel].dominates(this.labels[labels[i]])) {
		    this.marksuccessors(labels[i]);
		    if (i < labels.length - 1) {
		        labels[i] = labels[labels.length-1];
		    }
		    labels.pop();
	        } else {
		    i += 1;
	        }
	    }
	    // at this point newlabel is not dominated so we add it
	    labels.push(newlabel);
	    return true;
        }
    }
    
    function Label(at, visits, pred, cost, length, q) {
        this.at = at;
        this.visits = visits;
        this.pred = pred;
        this.cost = cost;
        this.length = length;
        this.q = q;
        this.ignore = false;
        this.successors = new Array();

        this.dominates = function(other) {
            if (this.cost > other.cost || this.length > other.length)
                return false;
            for (var i=0; i < n; i++) {
                if (this.visits[i] && ! other.visits[i]) return false;
            }
            for (var r=0; r < nresources; r++) {
                if (this.q[r] > other.q[r]) return false;
            }
            return true;
        }

        this.extend = function(fromindex, to) {
            var visits = this.visits.slice();
            visits[to] = true;
            var q = this.q.slice();
	    for (var r=0; r < nresources; r++) {
	        if ((to & (1 << r)) > 0) {
		    q[r] += 1;
	        }
	    }
            var nl = new Label(to,
                               visits,
                               fromindex,
                               this.cost + rc[this.at*n+to],
                               this.length + d[this.at*n+to],
                               q);
            return nl;
        }
    }
    
}

// C: capacity (flat) matrix
// F: flow (flat) matrix
// n: number of nodes in the graph
// s: source
// t: sink
function edmondskarp(C, F, n, s, t) {
    var totalflow = 0.0;
    var moreflow = true;
    var Q = new Array();
    var pred = new Array(n);
    for (var i=0; i < n; i++) { pred[i] = -1; }
    for (var i=0; i < n; i++) {
        for (var j=0; j < n; j++) {
            F[i*n+j] = 0.0;
        }
    }
    while (moreflow) {
        // reset predecessors
        for (var i=0; i < n; i++) {
            pred[i] = -1;
        }
        Q.push(s);
        while (Q.length > 0) {
            var cur = Q.shift();
            for (var j=0; j < n; j++) {
                if (j == cur) { continue; }
                if (pred[j] == -1 && j != s && C[cur*n+j] > F[cur*n+j]) {
                    pred[j] = cur;
                    Q.push(j);
                }
            }
        }
        // did we find an augmenting path?
        if (pred[t] != -1) {
            var df = Number.MAX_SAFE_INTEGER;
            var j = t;
            var i = pred[t];
            while (i != -1) {
                if (df > C[i*n+j] - F[i*n+j]) {
                    df = C[i*n+j] - F[i*n+j];
                }
                j = i;
                i = pred[i];
            }
            j = t;
            i = pred[t];
            while (i != -1) {
                F[i*n+j] += df;
                j = i;
                i = pred[i];
            }
            totalflow += df;
        } else {
            moreflow = false;
        }
    }
    return totalflow;
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
	} else if (tokens.length == n && d.length < n * n) {
	    d = d.concat(tokens.map(x => parseInt(x)));
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
	} else if (benchmarkname == 'lns') {
	    n = sol.lns();
	} else if (benchmarkname == 'espprc') {
	    n = sol.espprc(6, 1);
	} else if (benchmarkname == 'espprc-2') {
	    n = sol.espprc(6, 2);
	} else if (benchmarkname == 'espprc-index') {
	    n = sol.espprc(6, 1, true);
	} else if (benchmarkname == 'maxflow') {
	    n = sol.maxflow();
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
