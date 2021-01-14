struct TSPData{ T<:Real }
    n::Int    # number of nodes
    d::Matrix{T} # distance matrix
    aux::Matrix{Float64}  # auxiliary graph used e.g. in ESPPRC
    aux2::Matrix{Float64}  # auxiliary graph used e.g. in maxflow
end

include("espprc.jl")
include("espprc-index.jl")
include("maxflow.jl")

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
    aux = zeros(Float64, size(d))
    aux2 = zeros(Float64, size(d))
    data = TSPData{T}(n, d, aux, aux2)
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
        δ = d.d[s.tour[i-1], s.tour[i+l]] + d.d[s.tour[p], s.tour[i]] +
            d.d[s.tour[i+l-1], s.tour[p+1]] -
            d.d[s.tour[p], s.tour[p+1]] - d.d[s.tour[i-1], s.tour[i]] -
            d.d[s.tour[i+l-1], s.tour[i+l]]
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

function lns(d::TSPData{T}, sol::TSPSolution, niter::Int=10) where T
    checksum = zero(T)
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
            bestcost, bestfrom, bestto = typemax(T), 0, 0
            for from in 1:length(unplanned), to in 1:length(tmp)-1
                δ = d.d[tmp[to], unplanned[from]] +
                    d.d[unplanned[from], tmp[to+1]] -
                    d.d[tmp[to], tmp[to+1]]
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
                nresources::Int=6, resourcecapacity::Int=1,
                index::Bool=false) where T <: TSPData where ST <: TSPSolution
    dual = zeros(Float64, d.n)
    for (i, j) in @views zip(sol.tour[1:end-1], sol.tour[2:end])
        dual[j] = d.d[i, j]
    end
    for i ∈ 1:d.n, j ∈ 1:d.n
        d.aux[i, j] = d.d[i, j] - dual[j]
    end
    # max len: sum of best assignments
    maxlen = sum( [ minimum([d.d[i, j] for j ∈ 1:d.n if i ≠ j])
                    for i ∈ 1:d.n ] )
    e = ESPPRC(d, nresources, resourcecapacity, maxlen)
    if index
        Int(trunc(solvewithindex(e)))
    else
        Int(trunc(solve(e)))
    end
end

function maxflow(d::T, sol::ST) where T <: TSPData where ST <: TSPSolution
    t = zeros(Float64, d.n)
    for (i, j) ∈ @views zip(sol.tour[1:end-1], sol.tour[2:end])
        t[j] = d.d[i, j]
    end
    for i ∈ 1:d.n, j ∈ 1:d.n
        d.aux[i, j] = if (d.d[i, j] > t[j]) d.d[i,j]/1000 else zero(Float64) end
    end
    checksum = zero(Float64);
    for sink in 2:d.n
        mf = edmondskarp(d.aux, d.aux2, d.n, 1, sink)
        checksum += mf
    end
    Int(trunc(checksum))
end
