#!/bin/bash

dirname=`basename \`pwd\``

version=`java -version 2>&1 | head -n 1`

java TSPBenchmark $1 $2 | sed -e "s/java,/$dirname,/g" -e "s/,flat,/,flat,$version,/g" -e "s/,nested,/,nested,$version,/g"
