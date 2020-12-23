module TSPBenchmark

using CPUTime

export benchmark_many

include("tspdata.jl")
include("espprc.jl")

mutable struct TSPSolution
    tour::Vector{Int}
end

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

function two_opt(data::T, sol::TSPSolution) where T <: TSPData
    t = 0
    while first2eimprovement(data, sol)
        t += 1
    end
    return t
end

function first2eimprovement(d::T, sol::TSPSolution) where T
    for p1 in 1:length(sol.tour)-3, p2 in p1+2:length(sol.tour)-1
        if dist(d, sol.tour[p1], sol.tour[p1+1]) +
            dist(d, sol.tour[p2], sol.tour[p2+1]) >
            dist(d, sol.tour[p1], sol.tour[p2]) +
            dist(d, sol.tour[p1+1], sol.tour[p2+1])
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

function or_opt(data::T, sol::TSPSolution) where T
    t = 0
    while firstorimprovement(data, sol)
        t += 1
    end
    return t
end

function firstorimprovement(d::T, s::TSPSolution) where T
    for i in 2:length(s.tour)-1, l in 1:(min(3, length(s.tour)-i)),
        p in [ 1:i-2 ; i+l:length(s.tour)-1 ]
        #
        δ = dist(d, s.tour[i-1], s.tour[i+l]) + dist(d, s.tour[p], s.tour[i]) +
            dist(d, s.tour[i+l-1], s.tour[p+1]) -
            dist(d, s.tour[p], s.tour[p+1]) - dist(d, s.tour[i-1], s.tour[i]) -
            dist(d, s.tour[i+l-1], s.tour[i+l])
        # improvement found
        if δ < 0
            seq = [ k for k in s.tour[i:i+l-1] ]
            if i < p
                for j in i:p-l
                    s.tour[j] = s.tour[j+l]
                end
                for j in 1:l
                    s.tour[p+j-l] = seq[j]
                end
            else
                for j in i-1:-1:p+1
                    s.tour[j+l] = s.tour[j]
                end
                for j in 1:l
                    s.tour[p+j] = seq[j]
                end
            end
            return true
        end
    end
    return false
end

function lns(d::T, sol::TSPSolution, niter::Int=10) where T
    # ugly! is there an elegant Julia solution without writing more functions?
    ntype = typeof(d.d[1,1])
    #
    checksum = zero(ntype)
    for iter in 1:niter
        # step 0: copy incumbent
        tmp = copy(sol.tour)
        unplanned = Int[]
        # step 1: destroy
        t = 2
        while t < length(tmp)
            push!(unplanned, tmp[t])
            deleteat!(tmp, t)
            t += 1
        end
        # step 2: repair
        while length(unplanned) > 0
            bestcost, bestfrom, bestto = typemax(ntype), 0, 0
            for from in 1:length(unplanned), to in 1:length(tmp)-1
                δ = dist(d, tmp[to], unplanned[from]) +
                    dist(d, unplanned[from], tmp[to+1]) -
                    dist(d, tmp[to], tmp[to+1])
                if δ < bestcost
                    bestcost, bestfrom, bestto = δ, from, to
                end
            end
            # perform best found insertion
            insert!(tmp, bestto + 1, unplanned[bestfrom])
            deleteat!(unplanned, bestfrom)
            checksum += bestcost
        end
        # step 3: move to new incumbent
        sol.tour = tmp
    end
    checksum
end

function espprc(d::T, sol::ST;
                nresources::Int=6, resourcecapacity::Int=1) where T <: TSPData where ST <: TSPSolution
    dual = zeros(Float64, d.n)
    for (i, j) in zip(sol.tour[1:end-1], sol.tour[2:end])
        dual[j] = dist(d, i, j)
    end
    for i ∈ 1:d.n, j ∈ 1:d.n
        setaux!(d, i, j, dist(d, i, j) - dual[j])
    end
    # max len: sum of best assignments
    maxlen = sum( [ minimum([dist(d, i, j) for j ∈ 1:d.n if i ≠ j])
                    for i ∈ 1:d.n ] )
    e = ESPPRC(d, nresources, resourcecapacity, maxlen)
    solve(e)
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
            t = @CPUelapsed n = espprc(data, s, 6, 2,
                                       nresources=6, resourcecapacity=2)
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
