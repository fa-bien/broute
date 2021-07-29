# BROUTE

BROUTE is a benchmarking suite for routing optimization algorithms, see description here: https://arxiv.org/abs/2107.13492

## General structure

All implementations are a subdirectory of the `implementations` directory. New implementations should also go there.

Each implementation directory contains a script called `run_benchmark.sh` which takes two arguments: 
1. the directory containing input data files to consider for the benchmark
1. the benchmark name

For example to run the `c++98` implementation on the `lns` benchmark using files from directory `instances`:

`./implementations/c++98/run_benchmark.sh instances lns`

Optionally, implementation subdirectories can contain a script called `build.sh` that executes necessary steps that are prerequisites for that implementation (e.g. compilation or package installation).

## Running all benchmarks
Use `scripts/build_all.sh` to build all implementations.

Use `scripts/run_all.sh`, or `scripts/complete_all.sh` to generate only missing results. Both scripts look at the environment variable THREADS for parallelism.
For example, to run all implementations of all benchmarks with 4 parallel threads:
`THREADS=4 ./scripts/run_all.sh`

## Exploiting benchmark results

There are scripts in the `scripts` directory for the analysis of experimental results:

* `sanitycheck.py` takes CSV file names as command line parameters and checks that they all produce the same checksum values
* `compare.R` produces box plots like in the paper. Requires R. A directory containing CSV files must be provided as command line parameter.
* `profiles.py` produces performance profiles like in the paper. Requires matplotlib. A directory containing CSV files must be provided as command line parameter. The profiles are generated interactively: for each profile, the legend can be moved interactively then the PDF is generated when the window is closed.
