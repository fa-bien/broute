use std::collections::VecDeque;

use crate::tsp;

// d.aux contains capacities
// d.aux2 is used to store flow
// d.n is the number f nodes in the complete graph
// s is the source
// t is the sink
pub fn edmondskarp(d: &mut tsp::TSPData, s: usize, t: usize) -> f64 {
    let mut totalflow: f64 = 0.0;
    let mut moreflow: bool = true;
    let mut q: VecDeque<usize> = VecDeque::new();
    // MAX means nil i.e. "no predecessor"
    let mut pred: Vec<usize> = vec![usize::MAX; d.n];
    for i in 0..d.n {
        for j in 0..d.n {
            d.setaux2(i, j, 0.0);
        }
    }
    while moreflow {
        // reset predecessors
        for i in 0..d.n {
            pred[i] = usize::MAX;
        }
        q.push_back(s);
        while ! q.is_empty() {
            let cur = q.pop_front().unwrap();
            for j in 0..d.n {
                if j == cur { continue }
                if pred[j] == usize::MAX && j != s &&
                    d.aux(cur, j) > d.aux2(cur, j) {
                    pred[j] = cur;
                    q.push_back(j);
                }
            }
        }
        // did we find an augmenting path?
        if pred[t] != usize::MAX {
            let mut df = f64::MAX;
            let mut i = pred[t];
            let mut j = t;
            while i != usize::MAX {
                if df > d.aux(i, j) - d.aux2(i, j) {
                    df = d.aux(i, j) - d.aux2(i, j)
                }
                j = i;
                i = pred[i];
            }
            i = pred[t];
            j = t;
            while i != usize::MAX {
                d.setaux2(i, j, d.aux2(i, j) + df);
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
