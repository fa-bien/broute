module TSPBenchmark

using CPUTime
using StaticArrays

export benchmark_many

struct TSPData{ T<:Real }
    n::Int    # number of nodes
    d::Vector{T} # distance matrix
end

mutable struct TSPSolution
    tour::Vector{Int}
end

function dist(d::TSPData{T}, i::T2, j::T2) where T where T2
    d.d[i * d.n - d.n + j]
end

function read_data(fname::String, T::DataType=Int)
    lines = open(fname) do f
        collect(eachline(f))
    end
    n = 0
    drow = 1
    d = Vector{T}()
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
            d = zeros(T, n^2)
        elseif drow ≤ n
            row = [parse(T, x) for x in tokens]
            f = 1 + (n * (drow - 1))
            d[f:f + n - 1] = row
            drow += 1
        elseif length(solutions) ≤ nsols
            push!(solutions, TSPSolution([1+parse(Int, x) for x in tokens]))
        end
    end
    data = TSPData{T}(n, [x for x in d])
    return data, solutions
end

function two_opt(data::TSPData{T}, sol::TSPSolution) where T
    t = 0
    while first2eimprovement(data, sol)
        t += 1
    end
    return t
end

function first2eimprovement(d::TSPData{T}, sol::TSPSolution) where T
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

function or_opt(data::TSPData{T}, sol::TSPSolution) where T
    t = 0
    while firstorimprovement(data, sol)
        t += 1
    end
    return t
end

function firstorimprovement(d::TSPData{T}, s::TSPSolution) where T
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

# old less efficient version

# function firstorimprovement(d::TSPData{T}, s::TSPSolution) where T
#     for i in 2:length(s.tour)-1, l in 1:(min(3, length(s.tour)-i)),
#         p in [ 1:i-2 ; i+l:length(s.tour)-1 ]
#         #
#         δ = d.d[s.tour[i-1], s.tour[i+l]] + d.d[s.tour[p], s.tour[i]] +
#             d.d[s.tour[i+l-1], s.tour[p+1]] -
#             d.d[s.tour[p], s.tour[p+1]] - d.d[s.tour[i-1], s.tour[i]] -
#             d.d[s.tour[i+l-1], s.tour[i+l]]
#         # improvement found
#         if δ < 0
#             if i < p
#                 s.tour = [ s.tour[1:i-1] ; s.tour[i+l:p] ; s.tour[i:i+l-1] ;
#                            s.tour[p+1:end] ]
#             else
#                 s.tour = [ s.tour[1:p] ; s.tour[i:i+l-1] ; s.tour[p+1:i-1] ;
#                            s.tour[i+l:end] ]
#             end
#             return true
#         end
#     end
#     return false
# end

function benchmark_one(data::TSPData{T}, solutions::Vector{TSPSolution},
                       benchmarkname::String) where T
    totaltime = 0.0
    nimpr = 0
    for s in solutions
        if benchmarkname == "2-opt"
            t = @CPUelapsed n = two_opt(data, s)
        elseif lowercase(benchmarkname) == "or-opt"
            t = @CPUelapsed n = or_opt(data, s)
        else
            throw(ArgumentError("Unknown benchmark: $benchmarkname"))
        end
        totaltime += t
        nimpr += n
    end
    return nimpr, totaltime
end

function benchmark_many(dirname::String, benchmarkname::String="2-opt")
#    println("#language,version,benchmark,instance,n,nsolutions,n_improvements,time(s)")
    nimpr = 0
    for fname in readdir(dirname)
        d, sols = read_data(joinpath(dirname, fname), Int)
        n, l = benchmark_one(d, sols, benchmarkname)
        println(join((basename(pwd()), VERSION, benchmarkname, fname,
                      string(d.n),
                      string(size(sols,1)), string(n), string(l)),
                     ","))
        nimpr += n
    end
end

end # module
