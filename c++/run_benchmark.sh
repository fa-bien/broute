#!/bin/bash

dirname=`basename \`pwd\``

#echo "#language,instance,n,nsolutions,n_improvements,CPU"
for i in $1/*
do
    ./tspbenchmark $i | sed -e "s/c++/$dirname/g"
done
