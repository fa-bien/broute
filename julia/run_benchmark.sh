#!/bin/bash

julia --check-bounds=no --inline=yes -O3 tspbenchmark.jl $1
