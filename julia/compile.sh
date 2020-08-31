#!/bin/sh

julia -e "using Pkg; Pkg.activate(\"TSPBenchmark\"); Pkg.instantiate()" >&2
