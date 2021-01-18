#!/bin/bash

# Expectations: * a directory called 'implementations' contains the various
#                 implementations
#               * a directory called 'instances' contains all test instances
impldir=`pwd`'/implementations'
instdir=`pwd`'/instances'

# we do multi-threading!
# Number of threads = environment variable THREADS or default value
[[ -z "$THREADS" ]] && THREADS=3

all_langs="c++14 c++98 c++-hybrid-matrix c++-nested-matrix c++-static-arrays java java-nested-matrix javascript javascript-nested-matrix java-static-arrays julia-array julia-flat-matrix julia-square-matrix numba numba-flat-matrix numpy numpy-flat-matrix pypy pypy-nested-matrix python python-flat-matrix python-nested-matrix-function rust"
lns_langs="c++14 c++98 java javascript julia-array julia-flat-matrix julia-square-matrix pypy python rust"
espprc_langs="c++14 c++98 java javascript julia-array julia-flat-matrix julia-square-matrix pypy python"
espprcindex_langs="c++14 c++98 java javascript julia-array julia-flat-matrix julia-square-matrix pypy python rust"
maxflow_langs="c++14 c++98 java javascript julia-array julia-flat-matrix julia-square-matrix pypy python rust"
declare -A benchmarks=( ["2-opt"]=$all_langs
			["Or-opt"]=$all_langs
			["lns"]=$lns_langs
			["espprc"]=$espprc_langs
			["espprc-index"]=$espprcindex_langs
			["maxflow"]=$maxflow_langs
		      )

echo "Running benchmarks"
for benchmark in "${!benchmarks[@]}"; do
    for lang in ${benchmarks[$benchmark]}; do
	(echo -e "Running \e[1m$lang\e[0m implementation of \e[1m$benchmark\e[0m benchmark"
	 (pushd $impldir'/'$lang > /dev/null
	  # [[ -f build.sh ]] && ./build.sh
	  echo "language,version,benchmark,instance,n,nsolutions,checksum,time"
	  ./run_benchmark.sh $instdir $benchmark
	  popd > /dev/null
	 ) > $benchmark-$lang-runs.csv
	 echo "Done running $lang implementation of $benchmark"
	) &
	# parallelisation stolen from
	#https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop
	if [[ $(jobs -r -p | wc -l) -ge $THREADS ]]; then
            wait -n
	fi
    done
done

wait
echo "All languages done running"
