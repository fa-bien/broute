#!/bin/bash

languages='c++ c++-static c++98 julia rust java java-static numba javascript python pypy'
benchmarks='2-opt Or-opt'

(echo "language,version,benchmark,instance,n,nsolutions,checksum,time"
 for lang in $languages
 do
     cd $lang
     [[ -f compile.sh ]] && ./compile.sh
     for bench in $benchmarks
     do
	 ./run_benchmark.sh ../instances $bench
     done
     cd ..
 done) > allruns.csv
