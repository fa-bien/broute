function edmondskarp(C::MT, F::MT, n::Int, s::Int, t::Int) where MT
    totalflow = zero(Float64)
    moreflow = true
    Q = Deque{Int}()
    pred = [ -1 for i ∈ 1:n ]
    for i ∈ 1:n, j ∈ 1:n
        F[i,j] = zero(Float64)
    end
    while moreflow
        # reset predecessors
        for i ∈ 1:n
            pred[i] = -1
        end
        push!(Q, s)
        while ! isempty(Q)
            cur = popfirst!(Q)
            for j in 1:n
                j == cur && continue
                if pred[j] == -1 && j ≠ s && C[cur, j] > F[cur, j]
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
                if df > C[i,j] - F[i,j]
                    df = C[i,j] - F[i,j]
                end
                i, j = pred[i], i
            end
            i, j = pred[t], t
            while i ≠ -1
                F[i,j] += df
                i, j = pred[i], i
            end
            totalflow += df
        else
            moreflow = false
        end
    end
    totalflow
end
