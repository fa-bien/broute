use std::env;
use std::fs;
use regex::Regex;

// for time measurement
use cpu_time::ProcessTime;

struct TSPData {
    n: usize,
    d: Vec<u32>,
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
    //
    fn first_improvement(&mut self, data: &TSPData) -> bool {
        for p1 in 0..self.nodes.len()-3 {
            for p2 in p1+2..self.nodes.len()-1 {
                if data.d(self.nodes[p1], self.nodes[p1+1]) +
                    data.d(self.nodes[p2], self.nodes[p2+1]) >
                    data.d(self.nodes[p1], self.nodes[p2]) +
                    data.d(self.nodes[p1+1], self.nodes[p2+1]) {
                        for i in 0..((p2-p1+1)/2) {
                            let tmp = self.nodes[p1+1+i];
                            self.nodes[p1+1+i] = self.nodes[p2-i];
                            self.nodes[p2-i] = tmp;
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
    let flat = useful_data.replace("\n", " ");
    let tokens = flat.split(" ");
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
    return (TSPData{n: n, d: d}, solutions);
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

fn benchmark_many(dirname: &str) {
    let paths = fs::read_dir(dirname).unwrap_or_else(|error| {
        panic!("ERROR: {:?}\nDirectory not found: {:?}", error, dirname);
    });
    for path in paths {
        let base = path.unwrap();
        let t = base.path();
        let full_name = t.to_str().unwrap();
        let (data, mut solutions) = read_data(full_name);
        let (n, l) = benchmark_one(&data, &mut solutions);
        println!("rust,{},{},{},{},{}",
                 base.file_name().to_str().unwrap(),
                 data.n, solutions.len(), n, l);
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() == 2 {
        benchmark_many(&(args[1]));
    } else {
        println!("USAGE: {:} dir_name", args[0]);
        println!("{:?}", args.len());

        std::process::exit(1);
    }
}
