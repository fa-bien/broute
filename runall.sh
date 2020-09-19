#!/bin/bash

languages='c++ c++-static c++98 julia rust java java-static numba javascript python pypy'

benchmarks='2-opt Or-opt'

for lang in $languages
do
    echo "Running $lang"
    (cd $lang
     [[ -f compile.sh ]] && ./compile.sh
     echo "language,version,benchmark,instance,n,nsolutions,checksum,time"
     for bench in $benchmarks
     do
	 ./run_benchmark.sh ../instances $bench
     done
     cd ..
    ) > $lang-runs.csv
done
