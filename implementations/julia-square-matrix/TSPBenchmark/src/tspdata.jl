abstract type TSPData end

struct SquareMatrixTSPData{T} <: TSPData
    d::Matrix{T}
    n::Int
    aux::Matrix{Float64}
    aux2::Matrix{Float64}
end

struct FlatMatrixTSPData{T} <: TSPData
    d::Vector{T}
    n::Int
    aux::Vector{Float64}
    aux2::Vector{Float64}
end

function FlatMatrixTSPData(sm::Matrix{T}, n::Int) where T
    d = vec(transpose(sm))
    aux = zeros(Float64, length(d))
    aux2 = zeros(Float64, length(d))
    FlatMatrixTSPData{T}(d, n, aux, aux2)
end

function SquareMatrixTSPData(sm::Matrix{T}, n::Int) where T
    aux = zeros(Float64, size(sm))
    aux2 = zeros(Float64, size(sm))
    SquareMatrixTSPData{T}(sm, n, aux, aux2)
end

function dist(d::MT, i::IT, j::IT) where MT <: SquareMatrixTSPData where IT <: Integer
    d.d[i, j]
end

function dist(d::MT, i::IT, j::IT) where MT <: FlatMatrixTSPData where IT <: Integer
    d.d[i * d.n - d.n + j]
end

function setaux!(d::MT, i::IT, j::IT, val::T) where MT <: SquareMatrixTSPData where IT <: Integer where T
    d.aux[i,j] = val
end

function setaux!(d::MT, i::IT, j::IT, val::T) where MT <: FlatMatrixTSPData where IT <: Integer where T
    d.aux[i * d.n - d.n + j] = val
end

function getaux(d::MT, i::IT, j::IT) where MT <: SquareMatrixTSPData where IT <: Integer
    d.aux[i,j]
end

function getaux(d::MT, i::IT, j::IT) where MT <: FlatMatrixTSPData where IT <: Integer 
    d.aux[i * d.n - d.n + j]
end

function setaux2!(d::MT, i::IT, j::IT, val::T) where MT <: SquareMatrixTSPData where IT <: Integer where T
    d.aux2[i,j] = val
end

function setaux2!(d::MT, i::IT, j::IT, val::T) where MT <: FlatMatrixTSPData where IT <: Integer where T
    d.aux2[i * d.n - d.n + j] = val
end

function getaux2(d::MT, i::IT, j::IT) where MT <: SquareMatrixTSPData where IT <: Integer
    d.aux2[i,j]
end

function getaux2(d::MT, i::IT, j::IT) where MT <: FlatMatrixTSPData where IT <: Integer 
    d.aux2[i * d.n - d.n + j]
end

function addaux2!(d::MT, i::IT, j::IT, offset::FT) where MT <: FlatMatrixTSPData where IT <: Integer where FT <: Real
    d.aux2[i * d.n - d.n + j] += offset
end

function addaux2!(d::MT, i::IT, j::IT, offset::FT) where MT <: SquareMatrixTSPData where IT <: Integer where FT <: Real
    d.aux2[i, j] += offset
end
