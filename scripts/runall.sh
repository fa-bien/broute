#!/bin/bash

# Expectations: * a directory called 'implementations' contains the various
#                 implementations
#               * a directory called 'instances' contains all test instances
impldir=`pwd`'/implementations'
instdir=`pwd`'/instances'

# languages: list of command line arguments, or default list if no argument
defaultlanguages='c++ c++-static-arrays c++98 julia rust java java-static-arrays numba javascript python pypy'
languages="$@"
if [[ "$#" -lt 1 ]]; then
    languages=$defaultlanguages
fi

benchmarks='2-opt Or-opt lns'

# we do multi-threading!
# Number of threads = environment variable THREADS or default value
[[ -z "$THREADS" ]] && THREADS=3

for lang in $languages
do
    (echo "Running $lang"
     (pushd $impldir'/'$lang > /dev/null
      [[ -f compile.sh ]] && ./compile.sh
      echo "language,version,benchmark,instance,n,nsolutions,checksum,time"
      for bench in $benchmarks
      do
	  ./run_benchmark.sh $instdir $bench
      done
      popd > /dev/null
     ) > $lang-runs.csv
     echo "Done running $lang"
    ) &
    # parallelisation stolen from
    #https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop
    if [[ $(jobs -r -p | wc -l) -ge $THREADS ]]; then
        wait -n
    fi
done

wait
echo "All languages done running"
