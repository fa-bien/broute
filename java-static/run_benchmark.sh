#!/bin/bash

dirname=`basename \`pwd\``

java TSPBenchmark $1 | sed -e "s/java/$dirname/g"
