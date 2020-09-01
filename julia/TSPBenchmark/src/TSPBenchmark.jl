module TSPBenchmark

using CPUTime

export benchmark_many

struct TSPData{ T<:Real }
    n::Int    # number of nodes
    d::Matrix{T} # distance matrix
end

mutable struct TSPSolution
    tour::Vector{Int}
end

function read_data(fname::String, T::DataType=Int)
    lines = open(fname) do f
        collect(eachline(f))
    end
    n = 0
    drow = 1
    d = zeros(T, 1, 1)
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
            d = zeros(T, n, n)
        elseif drow ≤ n
            row = [parse(T, x) for x in tokens]
            d[drow,:] = row
            drow += 1
        elseif length(solutions) ≤ nsols
            push!(solutions, TSPSolution([1+parse(Int, x) for x in tokens]))
        end
    end
    data = TSPData{T}(n, d)
    return data, solutions
end

function two_opt(data::TSPData{T}, sol::TSPSolution) where T
    t = 0
    while first_improvement(data, sol)
        t += 1
    end
    return t
end

function first_improvement(d::TSPData{T}, sol::TSPSolution) where T
    for p1 in 1:length(sol.tour)-3, p2 in p1+2:length(sol.tour)-1
        if d.d[sol.tour[p1], sol.tour[p1+1]] +
            d.d[sol.tour[p2], sol.tour[p2+1]] >
            d.d[sol.tour[p1], sol.tour[p2]] +
            d.d[sol.tour[p1+1], sol.tour[p2+1]]
            # improving 2-exchange found
            for i in 0:(p2-p1+1) ÷ 2 - 1
                sol.tour[p1+1+i], sol.tour[p2-i] =
                    sol.tour[p2-i], sol.tour[p1+1+i]
            end
            return true
        end
    end
    return false
end

function benchmark_one(data::TSPData{T}, solutions::Vector{TSPSolution}) where T
    total2opttime = 0.0
    nimpr = 0
    for s in solutions
        t = @CPUelapsed n = two_opt(data, s)
        total2opttime += t
        nimpr += n
    end
    return nimpr, total2opttime
end

function benchmark_many(dirname::String, benchmarkname::String="2-opt")
#    println("#language,version,benchmark,instance,n,nsolutions,n_improvements,time(s)")
    nimpr = 0
    for fname in readdir(dirname)
        d, sols = read_data(joinpath(dirname, fname), Int)
        n, l = benchmark_one(d, sols)
        println(join((basename(pwd()), VERSION, benchmarkname, fname,
                      string(d.n),
                      string(size(sols,1)), string(n), string(l)),
                     ","))
        nimpr += n
    end
end

end # module
