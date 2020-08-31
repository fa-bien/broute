using Pkg
Pkg.activate("TSPBenchmark")
using TSPBenchmark

function main(ARGS)
    if length(ARGS) ≠ 1
        throw(ArgumentError("USAGE: tspbenchmark.jl tsp_data_file_dir"))
    else
        benchmark_many(ARGS[1])
    end
end

main(ARGS)
