use std::{cell::Cell};

use crate::tsp;
use std::collections::VecDeque;

struct Label {
    at: usize,
    visited: Vec<bool>,
    ignore: Cell<bool>,
    _predecessor: Option<usize>,
    cost: f64,
    length: i32,
    q: Vec<usize>,
    successors: Vec<usize>,
}

impl Label {
    fn dominates(&self, other: &Label) -> bool {
        if self.cost > other.cost || self.length > other.length {
            return false;
        }
        for (v1, v2) in self.visited.iter().zip(other.visited.iter()) {
            if v1 > v2 { return false}
        }
        for (q1, q2) in self.q.iter().zip(other.q.iter()) {
            if q1 > q2 { return false}
        }
        return true;
    }
}

struct LabelCollection {
    labels: Vec<Label>,
}

impl LabelCollection {
    fn empty_label(&mut self, d: &tsp::TSPData, nresources: usize) -> usize {
        let visited: Vec<bool> = vec![false; d.n];
        let q: Vec<usize> = vec![0; nresources];
        self.labels.push(Label {
            at: 0,
            visited: visited,
            ignore: Cell::new(false),
            _predecessor: None,
            cost: 0.0,
            length: 0,
            q: q,
            successors: Vec::new(),
        });
        return self.labels.len() - 1;
    }

    // from is the index of a Label
    // to is a node index
    fn extend(&mut self, d: &tsp::TSPData, from: usize, to: usize) -> usize {
        let mut visited = self.labels[from].visited.clone();
        visited[to] = true;
        let mut q = self.labels[from].q.clone();
        for i in 0..q.len() {
            if (to & (1 << i)) > 0 {
                q[i] += 1;
            }
        }
        let cost = self.labels[from].cost + d.aux(self.labels[from].at, to);
        let length = self.labels[from].length + d.d(self.labels[from].at, to);
        let nl = Label{at: to,
                       visited: visited,
                       ignore: Cell::new(false), 
                       _predecessor: Some(from),
                       cost: cost,
                       length: length,
                       q: q,
                       successors: Vec::new()};
        self.labels.push(nl);
        return self.labels.len() - 1;
    }

    // add label to as successor to label from
    fn addsuccessor(&mut self, from: usize, to: usize) {
        self.labels[from].successors.push(to);
    }
    
    fn marksuccessors(&self, index: usize) {
        let Label{ successors, .. } = &self.labels[index];
        for &s in successors {
            &self.labels[s].ignore.set(true);
            self.marksuccessors(s);
        }
    }

    fn updatedominance(&mut self, labels: &mut Vec<usize>, nlindex: usize) -> bool {
        let mut i: usize = 0;
        while i < labels.len() {
            if self.labels[labels[i]].dominates(&self.labels[nlindex]) {
                return false;
            }
            if self.labels[nlindex].dominates(&self.labels[labels[i]]) {
                self.marksuccessors(labels[i]);
                if i < labels.len() - 1 {
                    labels[i] = *labels.last().unwrap();
                }
                labels.pop();
            } else {
                i += 1;
            }
        }
        // at this point the new label is not dominated so we add it
        labels.push(nlindex);
        return true;
    }
}

pub fn solve(d: &tsp::TSPData,
             nresources: usize, resourcecapacity: usize, maxlen: i32) -> i32 {
    // we will store all labels here
    let mut lc = LabelCollection{ labels: Vec::new() };
    let mut q: VecDeque<usize> = VecDeque::new();
    let mut in_q: Vec<bool> = vec![false; d.n];
    // initial label
    let l0 = lc.empty_label(d, nresources);
    q.push_back(0);
    in_q[0] = true;
    // considered labels at each node
    let mut labels: Vec<Vec<usize>> = vec![Vec::new(); d.n];
    labels[0].push(l0);
    // main DP loop
    while ! q.is_empty() {
        let n = q.pop_front().unwrap();
        in_q[n] = false;
        for i in 0..labels[n].len() {
            let lind = labels[n][i];
            if lc.labels[lind].ignore.get() == true {
                continue;
            }
            for succ in 0..d.n {
                if lc.labels[lind].visited[succ] || succ == n { continue }
                // is the extension length-feasible?
                if lc.labels[lind].length + d.d(n, succ) + d.d(succ, 0)
                    > maxlen {
                        continue;
                    }
                // is it resource-feasible?
                let mut rfeas: bool = true;
                for r in 0..nresources {
                    if (succ & (1 << r)) > 0 &&
                        lc.labels[lind].q[r] + 1 > resourcecapacity {
                            rfeas = false;
                            break;
                        }
                }
                if ! rfeas { continue }
                // at this point we know the extension is feasible
                let nl = lc.extend(d, lind, succ);
                let added = lc.updatedominance(&mut labels[succ], nl);
                if added {
                    lc.addsuccessor(lind, nl);
                    if ! in_q[succ] && succ != 0 {
                        q.push_back(succ);
                        in_q[succ] = true;
                    }
                }
            }
            lc.labels[lind].ignore.set(true);
        }
    }
    let mut bestcost: f64 = lc.labels[labels[0][0]].cost;
    for i in 1..labels[0].len() {
        if lc.labels[labels[0][i]].cost < bestcost {
            bestcost = lc.labels[labels[0][i]].cost;
        }
    }
    return bestcost as i32;
}
