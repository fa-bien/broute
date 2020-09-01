#!/bin/bash

version='node '`node --version`

./tspbenchmark.js $1 | sed -e "s/javascript/javascript,$version/g"
