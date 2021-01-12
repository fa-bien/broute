module TSPBenchmark

using CPUTime

export benchmark_many

include("tspdata.jl")
include("tspsolution.jl")

# MT is the type of matrix representation to use for TSP data
function read_data(fname::String, DT::DataType=Int, MT=SquareMatrixTSPData)
    lines = open(fname) do f
        collect(eachline(f))
    end
    n = 0
    drow = 1
    d = zeros(DT, 1, 1)
    nsols = 0
    solutions = TSPSolution[]
    for line in lines
        line = replace(line, r"#.*" => "")
        tokens = split(line)
        if length(tokens) == 0
            continue
        elseif length(tokens) == 2 && n == 0
            n = parse(Int, tokens[1])
            nsols = parse(Int, tokens[2])
            d = zeros(DT, n, n)
        elseif drow ≤ n
            row = [parse(DT, x) for x in tokens]
            d[drow,:] = row
            drow += 1
        elseif length(solutions) ≤ nsols
            push!(solutions, TSPSolution([1+parse(Int, x) for x in tokens]))
        end
    end
    data = MT(d, n)
    return data, solutions
end

function benchmark_one(data::T, solutions::Vector{TSPSolution},
                       benchmarkname::String) where T
    totaltime = 0.0
    nimpr = 0
    for s in solutions
        if benchmarkname == "2-opt"
            t = @CPUelapsed n = two_opt(data, s)
        elseif lowercase(benchmarkname) == "or-opt"
            t = @CPUelapsed n = or_opt(data, s)
        elseif lowercase(benchmarkname) == "lns"
            t = @CPUelapsed n = lns(data, s)
        elseif lowercase(benchmarkname) == "espprc"
            t = @CPUelapsed n = espprc(data, s,
                                       nresources=6, resourcecapacity=1)
        elseif lowercase(benchmarkname) == "espprc-2"
            t = @CPUelapsed n = espprc(data, s,
                                       nresources=6, resourcecapacity=2)
        elseif lowercase(benchmarkname) == "espprc-index"
            t = @CPUelapsed n = espprc(data, s,
                                       nresources=6, resourcecapacity=1,
                                       index=true)
        elseif lowercase(benchmarkname) == "maxflow"
            t = @CPUelapsed n = maxflow(data, s)
        else
            throw(ArgumentError("Unknown benchmark: $benchmarkname"))
        end
        totaltime += t
        nimpr += n
    end
    return nimpr, totaltime
end

function benchmark_many(dirname::String, benchmarkname::String="2-opt",
                        MatrixType=SquareMatrixTSPData)
#    println("#language,version,benchmark,instance,n,nsolutions,n_improvements,time(s)")
    nimpr = 0
    for fname in readdir(dirname)
        d, sols = read_data(joinpath(dirname, fname), Int, MatrixType)
        n, l = benchmark_one(d, sols, benchmarkname)
        println(join((basename(pwd()), VERSION, benchmarkname, fname,
                      string(d.n),
                      string(size(sols,1)), string(n), string(l)),
                     ","))
        nimpr += n
    end
end

end # module
