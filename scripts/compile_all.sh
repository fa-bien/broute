#!/bin/bash

# Expectation: * a directory called 'implementations' contains the various
#                 implementations
impldir=`pwd`'/implementations'

# we do multi-threading!
# Number of threads = environment variable THREADS or default value
[[ -z "$THREADS" ]] && THREADS=3

langs="c++ c++98 c++-hybrid-matrix c++-nested-matrix c++-static-arrays java java-nested-matrix javascript javascript-nested-matrix java-static-arrays julia-array julia-flat-matrix julia-square-matrix numba numba-flat-matrix numpy numpy-flat-matrix pypy pypy-nested-matrix python python-flat-matrix python-nested-matrix-function rust"

echo "Compiling stuff"
for lang in $langs; do
    (echo -e "Compiling \e[1m$lang\e[0m implementation"
     pushd $impldir'/'$lang > /dev/null
     [[ -f compile.sh ]] && ./compile.sh
     popd > /dev/null
     echo -e "Done compiling \e[1m$lang\e[0m "
    ) &
    # parallelisation stolen from
    #https://unix.stackexchange.com/questions/103920/parallelize-a-bash-for-loop
    if [[ $(jobs -r -p | wc -l) -ge $THREADS ]]; then
        wait -n
    fi
done

wait
echo "All implementations compiled"
