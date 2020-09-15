#!/bin/bash

# call this script with the COMPILER env. variable set to the wanted compiler
# if none is specified, g++ is used
# example: COMPILER=clang++ ./compile.sh

COMPILER=${COMPILER:-g++}

$COMPILER -DCOMPILER=\"$COMPILER\" -Wall -ansi -pedantic -O3 -std=c++14 main.cpp -o tspbenchmark
