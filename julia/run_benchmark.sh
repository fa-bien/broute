#!/bin/bash

#julia --check-bounds=no --inline=yes -O3 tspbenchmark.jl $1

# only works from Julia 1.5 on
julia --check-bounds=no --inline=yes -O3 -t 1 tspbenchmark.jl $1
