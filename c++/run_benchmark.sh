#!/bin/bash

#echo "#language,instance,n,nsolutions,n_improvements,CPU"
for i in $1/*
do
    ./tspbenchmark $i
done
