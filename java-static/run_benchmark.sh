#!/bin/bash

dirname=`basename \`pwd\``

version=`java -version 2>&1 | head -n 1`

java TSPBenchmark $1 | sed -e "s/java/$dirname,$version/g"
