use std::env;
use std::fs;
use regex::Regex;

// for time measurement
use cpu_time::ProcessTime;

use rustc_version_runtime::version;

mod tsp;
mod espprc;

fn read_data(fname: &str) -> (tsp::TSPData, Vec<tsp::TSPSolution>) {
    let data = fs::read_to_string(fname).expect("Unable to read file");
    // remove comments
    let comm = Regex::new(r"#[^\n]*\n").unwrap();
    let useful_data = comm.replace_all(&data, "");
    // remove newlines
    let tokens = useful_data.split_whitespace();
    let mut n: usize = 0;
    let mut nsols: usize = 0;
    let mut d: Vec<i32> = Vec::<i32>::new();
    let mut aux: Vec<f64> = Vec::<f64>::new();
    let mut solutions: Vec<tsp::TSPSolution> = Vec::<tsp::TSPSolution>::new();
    let mut current_sol = tsp::TSPSolution{nodes: Vec::<usize>::new()};
    for tok in tokens {
        // header
        if n == 0 {
            n = tok.parse().unwrap();
        } else if nsols == 0 {
            nsols = tok.parse().unwrap();
        } else if d.len() < n * n {
            // distance matrix
            d.push(tok.parse().unwrap());
            aux.push(0.0);
        } else if solutions.len() < nsols {
            // reading a solution
            current_sol.nodes.push(tok.parse().unwrap());
            // did we complete a solution?
            if current_sol.nodes.len() == n + 1 {
                solutions.push(current_sol);
                current_sol = tsp::TSPSolution{nodes: Vec::<usize>::new()};
            }
        }
    }
    return (tsp::TSPData{n: n,
                         d: d.into_boxed_slice(),
                         aux: aux.into_boxed_slice()},
            solutions);
}

fn benchmark_one(data: &mut tsp::TSPData, solutions: &mut Vec<tsp::TSPSolution>,
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
        } else if benchmarkname == "lns" {
            cnt = sol.lns(data, 10);
        } else if benchmarkname == "espprc" {
            cnt = sol.espprc(data, 6, 1);
        } else if benchmarkname == "espprc-2" {
            cnt = sol.espprc(data, 6, 2);
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
        let (mut data, mut solutions) = read_data(full_name);
        let (n, l) = benchmark_one(&mut data, &mut solutions, benchmarkname);
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
