using Pkg
Pkg.activate("TSPBenchmark")
using TSPBenchmark

function main(ARGS)
    benchmarkname = "2-opt"
    if length(ARGS) < 1
        throw(ArgumentError("USAGE: tspbenchmark.jl tsp_data_file_dir [benchmark]"))
    else
        if length(ARGS) > 1
            benchmarkname = ARGS[2]
        end
        benchmark_many(ARGS[1], benchmarkname)
    end
end

main(ARGS)
