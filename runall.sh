#!/bin/bash

(echo "language,instance,n,nsolutions,n_improvements,CPU_2opt"
 for lang in c++ c++98 c++-static java java-static julia #javascript python numba pypy c++-clang c++-static-clang 
 do
     cd $lang
     [[ -f compile.sh ]] && ./compile.sh
     ./run_benchmark.sh ../instances
     cd ..
 done) > allruns.csv
