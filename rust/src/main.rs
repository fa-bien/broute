use std::env;
use std::fs;
use regex::Regex;

// for time measurement
use cpu_time::ProcessTime;

use rustc_version_runtime::version;

struct TSPData {
    n: usize,
    d: Box<[u32]>,
}

impl TSPData {
    fn d(&self, i: usize, j:usize) -> u32 { self.d[i * self.n + j] }
}

struct TSPSolution {
    nodes: Vec<usize>,
}

impl TSPSolution {
    fn two_opt(&mut self, data: &TSPData) -> u32 {
        let mut t = 0;
        while self.first_improvement(&data) { t += 1; }
        return t;
    }
    
    fn first_improvement(&mut self, data: &TSPData) -> bool {
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
    let mut d: Vec<u32> = Vec::<u32>::new();
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

fn benchmark_one(data: &TSPData, solutions: &mut Vec<TSPSolution>)
                 -> (u32, f64) {
    let mut count = 0;
    let mut total2opttime: f64 = 0.0;
    for sol in solutions {
        let t1 = ProcessTime::now();
        let cnt = sol.two_opt(data);
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
        let (n, l) = benchmark_one(&data, &mut solutions);
        println!("rust,{},{},{},{},{},{},{}",
                 version(), benchmarkname,
                 base.file_name().to_str().unwrap(),
                 data.n, solutions.len(), n, l);
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() == 2 {
        benchmark_many(&(args[1]), "2-opt");
    } else {
        println!("USAGE: {:} dir_name", args[0]);
        println!("{:?}", args.len());

        std::process::exit(1);
    }
}
