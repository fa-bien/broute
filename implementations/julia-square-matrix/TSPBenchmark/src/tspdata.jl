abstract type TSPData end

struct SquareMatrixTSPData{T} <: TSPData
    d::Matrix{T}
    n::Int
end

struct FlatMatrixTSPData{T} <: TSPData
    d::Vector{T}
    n::Int
end

function FlatMatrixTSPData(sm::Matrix{T}, n::Int) where T
    d = vec(transpose(sm))
    FlatMatrixTSPData{T}(d, n)
end

function dist(d::MT, i::IT, j::IT) where MT <: SquareMatrixTSPData where IT <: Integer
    d.d[i, j]
end

function dist(d::MT, i::IT, j::IT) where MT <: FlatMatrixTSPData where IT <: Integer
    d.d[i * d.n - d.n + j]
end
