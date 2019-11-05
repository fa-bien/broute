#!/bin/bash

(echo "language,instance,n,nsolutions,n_improvements,CPU_2opt"
 for lang in c++ c++98 julia rust c++-static java #java-static numba javascript python pypy
 do
     cd $lang
     [[ -f compile.sh ]] && ./compile.sh
     ./run_benchmark.sh ../instances
     cd ..
 done) > allruns.csv
