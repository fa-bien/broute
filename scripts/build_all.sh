#!/bin/bash

# Expectation: * a directory called 'implementations' contains the various
#                 implementations
impldir=`pwd`'/implementations'

# we do multi-threading!
# Number of threads = environment variable THREADS or default value
[[ -z "$THREADS" ]] && THREADS=3

langs="c++14 c++98 c++14-hybrid-matrix c++14-nested-matrix c++14-static-arrays java java-nested-matrix javascript javascript-nested-matrix java-static-arrays julia-array julia-flat-matrix julia-square-matrix numba numba-flat-matrix numpy numpy-flat-matrix pypy pypy-nested-matrix python python-flat-matrix python-nested-matrix-function rust"

echo "Building stuff"
for lang in $langs; do
    (echo -e "Building \e[1m$lang\e[0m implementation"
     pushd $impldir'/'$lang > /dev/null
     [[ -f build.sh ]] && ./build.sh
     popd > /dev/null
     echo -e "Done building \e[1m$lang\e[0m "
    ) &
    # parallelisation stolen from
    #https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop
    if [[ $(jobs -r -p | wc -l) -ge $THREADS ]]; then
        wait -n
    fi
done

wait
echo "All implementations compiled"
