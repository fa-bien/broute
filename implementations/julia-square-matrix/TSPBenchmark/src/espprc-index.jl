using DataStructures

mutable struct LabelWithIndex{ T <: Real }
    at::Int
    visits::Vector{Bool}
    ignore::Bool
    pred::Union{Nothing,Int}
    cost::Float64
    length::T
    q::Vector{Int}
    successors::Vector{Int}
end

function dominates(l1::T, l2::T) where T <: LabelWithIndex
    if l1.cost > l2.cost || l1.length > l2.length
        return false
    end
    for (v1, v2) ∈ zip(l1.visits, l2.visits)
        if v1 > v2
            return false
        end
    end
    for (r1, r2) in zip(l1.q, l2.q)
        if r1 > r2
            return false
        end
    end
    true
end

mutable struct LabelCollection{ T <: Real }
    labels::Vector{LabelWithIndex{T}}
end

# create empty label
function LabelWithIndex(d::MT, nresources::Int) where MT <: TSPData
    LabelWithIndex(1, zeros(Bool, d.n), false, nothing, 0.0, 0,
                   zeros(Int, nresources), zeros(Int, 0))
end

# create empty label and add it to lc
function emptylabel(d::DT, lc::LCT, nresources::Int) where DT <: TSPData where LCT <: LabelCollection
    push!(lc.labels, LabelWithIndex(d, nresources))
    return length(lc.labels)
end

# extend label and add it to LC
function extendlabel(d::MT, lc::LC, from::Int, to::Int) where MT <: TSPData where LC <: LabelCollection
    visits = copy(lc.labels[from].visits)
    visits[to] = true
    q = [ (((to-1) & 1 << (i-1)) > 0) ? r + 1 : r
          for (i,r) in enumerate(lc.labels[from].q) ]
    nl = LabelWithIndex(to, visits, false, from,
                        lc.labels[from].cost + getaux(d, lc.labels[from].at,to),
                        lc.labels[from].length + dist(d, lc.labels[from].at,to),
                        q,
                        zeros(Int, 0))
    push!(lc.labels, nl)
    return length(lc.labels)
end

function marksuccessors!(lc::LC, index::Int) where LC <: LabelCollection
    let l = lc.labels[index]
        for s ∈ l.successors
            lc.labels[s].ignore = true
            marksuccessors!(lc, s)
        end
    end
end

# update given list of labels with new label
# returns true if newlabel is added, false otherwise
function updatedominance!(lc::LCT, labels::Vector{Int}, newlabel::Int) where LCT <: LabelCollection
    i = 1
    while i ≤ length(labels)
        if dominates(lc.labels[labels[i]], lc.labels[newlabel])
            return false
        end
        if dominates(lc.labels[newlabel], lc.labels[labels[i]])
            marksuccessors!(lc, labels[i])
            if i < length(labels)
                labels[i] = labels[end]
            end
            pop!(labels)
        else
            i += 1
        end
    end
    # at this point we know that newlabel is not dominated, so we add it
    push!(labels, newlabel)
    true
end

function solvewithindex(e::ESPPRC{MT, T}) where MT <: TSPData where T <: Real
    # we store all labels here
    lc = LabelCollection(LabelWithIndex{T}[])
    # initial label
    l = emptylabel(e.d, lc, e.nresources)
    Q = Deque{Int}()
    inQ = zeros(Bool, e.d.n)
    push!(Q, 1)
    inQ[1] = true
    labels = [ Vector{Int}() for i in 1:e.d.n ]
    push!(labels[1], l)
    # main DP loop
    while ! isempty(Q)
        n = popfirst!(Q)
        inQ[n] = false
        for lindex ∈ labels[n]
            lc.labels[lindex].ignore && continue
            for succ ∈ 1:e.d.n
                (lc.labels[lindex].visits[succ] || succ == n) && continue
                # is it length-feasible?
                if lc.labels[lindex].length + dist(e.d, n, succ) + dist(e.d, succ, 1) > e.maxlen
                    continue
                end
                # is it resource-feasible?
                rfeas = true
                for (r, q) ∈ enumerate(lc.labels[lindex].q)
                    if ((succ-1) & (1 << (r-1))) > 0 &&
                        q + 1 > e.resourcecapacity
                        rfeas = false
                        break
                    end
                end
                rfeas || continue
                # at this point we know the extension is feasible so we do it
                nl = extendlabel(e.d, lc, lindex, succ)
                added = updatedominance!(lc, labels[succ], nl)
                added && push!(lc.labels[lindex].successors, nl)
                if added && (! inQ[succ]) && succ ≠ 1
                    push!(Q, succ)
                    inQ[succ] = true
                end
            end
            lc.labels[lindex].ignore = true
        end
    end
    Int(trunc(minimum(lc.labels[lindex].cost for lindex in labels[1])))
end
