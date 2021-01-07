use std::cmp::min;

use crate::espprc;

pub struct TSPData {
    pub n: usize,
    pub d: Box<[i32]>,
    pub aux: Box<[f64]>,
}

impl TSPData {
    pub fn d(&self, i: usize, j:usize) -> i32 { self.d[i * self.n + j] }

    pub fn aux(&self, i: usize, j:usize) -> f64 { self.aux[i * self.n + j] }
    
    pub fn setaux(&mut self, i: usize, j:usize, val:f64) {
        self.aux[i * self.n + j] = val;
    }
}

pub struct TSPSolution {
    pub nodes: Vec<usize>,
}

impl TSPSolution {
    pub fn two_opt(&mut self, data: &TSPData) -> i32 {
        let mut t = 0;
        while self.first_2e_improvement(&data) { t += 1; }
        return t;
    }
    
    fn first_2e_improvement(&mut self, data: &TSPData) -> bool {
        for (p1, n1) in self.nodes.windows(2).enumerate() {
            let (s1, t1) = (n1[0], n1[1]);
            for (p2, n2) in self.nodes.windows(2).enumerate().skip(p1 + 2) {
                let (s2, t2) = (n2[0], n2[1]);
                if data.d(s1, t1) + data.d(s2, t2) >
                    data.d(s1, s2) + data.d(t1, t2) {
                        for i in 0..((p2 - p1 + 1) / 2) {
                            self.nodes.swap(p1 + 1 + i, p2 - i);
                        }
                        return true;
                    }
            }
        }
        return false;
    }

    pub fn or_opt(&mut self, data: &TSPData) -> i32 {
        let mut t = 0;
        while self.first_or_improvement(&data) { t += 1; }
        return t;
    }

    fn or_delta(&self, data: &TSPData,
                ipred: usize, inode:usize,
                enode:usize, esucc:usize,
                pnode:usize, psucc:usize) -> i32 {
        return data.d(ipred, esucc) + data.d(pnode, inode)
            + data.d(enode, psucc) - data.d(pnode, psucc)
            - data.d(ipred, inode) - data.d(enode, esucc);
    }
    
    fn first_or_improvement(&mut self, data: &TSPData) -> bool {
        for (iminus, n1) in self.nodes.windows(2).enumerate() {
            let (ipred, inode) = (n1[0], n1[1]);
            for l in 1..(1 + min(3, self.nodes.len() - iminus - 2)) {
                let (enode, esucc) = (self.nodes[iminus+l],
                                      self.nodes[iminus+l+1]);
                for (p, n2) in self.nodes.windows(2).enumerate().take(iminus){
                    let (pnode, psucc) = (n2[0], n2[1]);
                    let delta = self.or_delta(data, ipred, inode, enode, esucc,
                                              pnode, psucc);
                    if delta < 0 {
			// first copy sequence we want to move
                        let mut t = vec![0; l];
                        t.clone_from_slice(&self.nodes[iminus+1..iminus+l+1]);
			// next move around what will end up being right of it
                        self.nodes.copy_within(p+1..iminus+1, p+1+l);
			// finally write in the sequence being moved
                        self.nodes[p+1..p+l+1].copy_from_slice(&t);
                        return true;
                    }
                }
                for (p, n2) in self.nodes.windows(2).enumerate().skip(iminus+1+l){
                    let (pnode, psucc) = (n2[0], n2[1]);
                    let delta = self.or_delta(data, ipred, inode, enode, esucc,
                                              pnode, psucc);
                    if delta < 0 {
			// first copy sequence we want to move
                        let mut t = vec![0; l];
                        t.clone_from_slice(&self.nodes[iminus+1..iminus+l+1]);
			// next move around what will end up being left of it
                        self.nodes.copy_within(iminus+1+l..p+1, iminus+1);
                        // finally write in the sequence being moved
                        self.nodes[p-l+1..p+1].copy_from_slice(&t);
                        return true;
                    }
                }
            }
        }
        return false;
    }

    pub fn lns(&mut self, data: &TSPData, niter: i32) -> i32 {
        let mut checksum: i32 = 0;
        for _iter in 1..(niter+1) {
            // step 0: copy incumbent
            let mut tmp = self.nodes.clone();
            let mut unplanned = Vec::new();
            // step 1: destroy
            let mut t = 1;
            while t < tmp.len() -1 {
                unplanned.push(tmp[t]);
                tmp.remove(t);
                t += 1;
            }
            // step 2: repair
            while unplanned.len() > 0 {
                let mut bestfrom: usize = 0;
                let mut bestto: usize = 0;
                let mut bestcost: i32 = i32::MAX;
                for (fro, k) in unplanned.iter().enumerate() {
                    for (to, ij) in tmp.windows(2).enumerate() {
                        let (i, j) = (ij[0], ij[1]);
                        let delta = data.d(i, *k) + data.d(*k, j) - data.d(i, j);
                        if delta < bestcost {
                            bestcost = delta;
                            bestfrom = fro;
                            bestto = to;
                        }
                    }
                }
		// perform best found insertion
		tmp.insert(bestto + 1, unplanned[bestfrom]);
		unplanned.remove(bestfrom);
		checksum += bestcost;
            }
            // step 3: set new incumbent
            self.nodes = tmp;
        }
        return checksum;
    }

    pub fn espprc(&self, data: &mut TSPData,
                  nresources: usize, resourcecapacity: usize) -> i32 {
        let mut dual = vec![0; data.n];
        for ij in self.nodes.windows(2) {
            let (i, j) = (ij[0], ij[1]);
            dual[j] = data.d(i, j);
        }
        for i in 0..data.n {
            for j in 0..data.n {
                data.setaux(i, j, f64::from(data.d(i, j) - dual[j]));
            }
        }
        // max len: sum over best assignment for each node
        let mut maxlen: i32 = 0;
        for i in 0..data.n {
            let mut best = i32::MAX;
            for j in 0..data.n {
                if i == j { continue }
                if data.d(i, j) < best {
                    best = data.d(i, j);
                }
            }
            maxlen += best;
        }
        return espprc::solve(data, nresources, resourcecapacity, maxlen);
    }
}
