#!/bin/bash

version='node '`node --version`
dirname=`basename \`pwd\``

for i in $1/*
do
    ./tspbenchmark.js $i $2 | sed -e "s/javascript/$dirname/g" -e "s/,flat,/,flat,$version/g" -e "s/,nested,/,nested,$version/g"
done
