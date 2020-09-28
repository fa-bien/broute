#!/bin/bash

version='node '`node --version`
dirname=`basename \`pwd\``

for i in $1/*
do
    ./tspbenchmark.js $i $2 | sed -e "s/javascript/$dirname,$version/g"
done
