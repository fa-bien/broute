use std::env;
use std::fs;
use regex::Regex;

// for time measurement
use cpu_time::ProcessTime;

use rustc_version_runtime::version;
use std::cmp::min;

struct TSPData {
    n: usize,
    d: Box<[i32]>,
}

impl TSPData {
    fn d(&self, i: usize, j:usize) -> i32 { self.d[i * self.n + j] }
}

struct TSPSolution {
    nodes: Vec<usize>,
}

impl TSPSolution {
    fn two_opt(&mut self, data: &TSPData) -> i32 {
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

    fn or_opt(&mut self, data: &TSPData) -> i32 {
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
    
}

fn read_data(fname: &str) -> (TSPData, Vec<TSPSolution>) {
    let data = fs::read_to_string(fname).expect("Unable to read file");
    // remove comments
    let comm = Regex::new(r"#[^\n]*\n").unwrap();
    let useful_data = comm.replace_all(&data, "");
    // remove newlines
    let tokens = useful_data.split_whitespace();
    let mut n: usize = 0;
    let mut nsols: usize = 0;
    let mut d: Vec<i32> = Vec::<i32>::new();
    let mut solutions: Vec<TSPSolution> = Vec::<TSPSolution>::new();
    let mut current_sol = TSPSolution{nodes: Vec::<usize>::new()};
    for tok in tokens {
        // header
        if n == 0 {
            n = tok.parse().unwrap();
        } else if nsols == 0 {
            nsols = tok.parse().unwrap();
        } else if d.len() < n * n {
            // distance matrix
            d.push(tok.parse().unwrap());
        } else if solutions.len() < nsols {
            // reading a solution
            current_sol.nodes.push(tok.parse().unwrap());
            // did we complete a solution?
            if current_sol.nodes.len() == n + 1 {
                solutions.push(current_sol);
                current_sol = TSPSolution{nodes: Vec::<usize>::new()};
            }
        }
    }
    return (TSPData{n: n, d: d.into_boxed_slice()}, solutions);
}

fn benchmark_one(data: &TSPData, solutions: &mut Vec<TSPSolution>,
                 benchmarkname: &str)
                 -> (i32, f64) {
    let mut count = 0;
    let mut total2opttime: f64 = 0.0;
    for sol in solutions {
        let cnt;
        let t1 = ProcessTime::now();
        if benchmarkname == "2-opt" {
            cnt = sol.two_opt(data);
        } else if benchmarkname == "Or-opt" {
            cnt = sol.or_opt(data);
        } else {
            panic!("Unknown benchmark: {:?}", benchmarkname);
        }
        let elapsed: f64 = t1.elapsed().as_secs_f64();
        total2opttime += elapsed;
        count += cnt;
    }
    (count, total2opttime)
}

fn benchmark_many(dirname: &str, benchmarkname: &str) {
    let paths = fs::read_dir(dirname).unwrap_or_else(|error| {
        panic!("ERROR: {:?}\nDirectory not found: {:?}", error, dirname);
    });
    for path in paths {
        let base = path.unwrap();
        let t = base.path();
        let full_name = t.to_str().unwrap();
        let (data, mut solutions) = read_data(full_name);
        let (n, l) = benchmark_one(&data, &mut solutions, benchmarkname);
        println!("rust,{},{},{},{},{},{},{}",
                 version(), benchmarkname,
                 base.file_name().to_str().unwrap(),
                 data.n, solutions.len(), n, l);
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let mut benchmarkname: &str = "2-opt";
    if args.len() > 1 {
        if args.len() > 2 {
            benchmarkname = &(args[2]);
        }
        benchmark_many(&(args[1]), &benchmarkname);
    } else {
        println!("USAGE: {:} dir_name", args[0]);
        println!("{:?}", args.len());

        std::process::exit(1);
    }
}
