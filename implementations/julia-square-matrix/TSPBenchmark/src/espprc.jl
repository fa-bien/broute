using DataStructures

mutable struct Label{ T <: Real, VB <: Vector{Bool}, VT <: Vector }
    at::Int
    visits::VB
    ignore::Bool
    pred::Union{Nothing,Label}
    cost::Float64
    length::T
    q::Vector{Int}
    successors::VT
end

# label extension
function Label(d::MT, l::LT, at::Int) where MT <: TSPData where LT <: Label
    visits = copy(l.visits)
    visits[at] = true
    q = [ (((at-1) & 1 << (i-1)) > 0) ? r + 1 : r for (i,r) in enumerate(l.q) ]
    Label(at, visits, false, l,
          l.cost + getaux(d, l.at, at), l.length + dist(d, l.at, at), q, [])
end

# create empty label
function Label(d::MT, nresources::Int) where MT <: TSPData
    Label(1, zeros(Bool, d.n), false, nothing, 0.0, 0,
          [0 for i in 1:nresources], [])
end

function dominates(l1::T, l2::T) where T <: Label
    if l1.cost > l2.cost || l1.length > l2.length
        return false
    end
    for v ∈ l1.visits
        if v ∉ l2.visits
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

function marksuccessors(l::LT) where LT <: Label
    for s ∈ l.successors
        s.ignore = true
        marksuccessors(s)
    end
end

# update given list of labels with new label
# returns true if newlabel is added, false otherwise
function update!(labels::Vector{LT}, newlabel::LT) where LT <: Label
    i = 1
    while i ≤ length(labels)
        if dominates(labels[i], newlabel)
            return false
        end
        if dominates(newlabel, labels[i])
            marksuccessors(labels[i])
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

struct ESPPRC{ MT <: TSPData, T <: Real }
    d::MT
    nresources::Int
    resourcecapacity::Int
    maxlen::T
end

function solve(e::ESPPRC{MT, T}) where MT <: TSPData where T <: Real
    # initial label
    l = Label(e.d, e.nresources)
    Q = Deque{Int}()
    inQ = zeros(Bool, e.d.n)
    push!(Q, 1)
    inQ[1] = true
    labels = [ Vector{Label{T, Vector{Bool}}}() for i in 1:e.d.n ]
    push!(labels[1], l)
    # main DP loop
    while ! isempty(Q)
        n = popfirst!(Q)
        inQ[n] = false
        for label ∈ labels[n]
            label.ignore && continue
            for succ ∈ 1:e.d.n
                (label.visits[succ] || succ == n) && continue
                # is it length-feasible?
                if label.length + dist(e.d, n, succ) + dist(e.d, succ, 1) >
                    e.maxlen
                    continue
                end
                # is it resource-feasible?
                rfeas = true
                for r ∈ 1:e.nresources
                    if ((succ-1) & (1 << (r-1))) > 0 &&
                        label.q[r] + 1 > e.resourcecapacity
                        rfeas = false
                        break
                    end
                end
                rfeas || continue
                # at this point we know the extension is feasible so we do it
                nl = Label(e.d, label, succ)
                added = update!(labels[succ], nl)
                added && push!(label.successors, nl)
                if added && (! inQ[succ]) && succ ≠ 1
                    push!(Q, succ)
                    inQ[succ] = true
                end
            end
            label.ignore = true
        end
    end
    Int(trunc(minimum(label.cost for label in labels[1])))
end
