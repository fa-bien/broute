function edmondskarp(d::MT, s::Int, t::Int) where MT <: TSPData
    totalflow = zero(Float64)
    moreflow = true
    Q = Deque{Int}()
    pred = [ -1 for i ∈ 1:d.n ]
    for i ∈ 1:d.n, j ∈ 1:d.n
        setaux2!(d, i, j, zero(Float64))
    end
    while moreflow
        # reset predecessors
        for i ∈ 1:d.n
            pred[i] = -1
        end
        push!(Q, s)
        while ! isempty(Q)
            cur = popfirst!(Q)
            for j in 1:d.n
                j == cur && continue
                if pred[j] == -1 && j ≠ s && getaux(d,cur,j) > getaux2(d,cur,j)
                    pred[j] = cur
                    push!(Q, j)
                end
            end
        end
        # did we find an augmenting path?
        if pred[t] ≠ -1
            df = typemax(Float64)
            i, j = pred[t], t
            while i ≠ -1
                if df > getaux(d, i, j) - getaux2(d, i, j)
                    df = getaux(d, i, j) - getaux2(d, i, j)
                end
                i, j = pred[i], i
            end
            i, j = pred[t], t
            while i ≠ -1
                addaux2!(d, i, j, df)
                i, j = pred[i], i
            end
            totalflow += df
        else
            moreflow = false
        end
    end
    totalflow
end
