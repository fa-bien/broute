#!/bin/bash

(echo "language,version,benchmark,instance,n,nsolutions,nimprovements,time(s)"
 for lang in c++ c++-static c++98 julia rust java java-static numba javascript python pypy
 do
     cd $lang
     [[ -f compile.sh ]] && ./compile.sh
     ./run_benchmark.sh ../instances
     cd ..
 done) > allruns.csv
