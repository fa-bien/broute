#!/usr/bin/env python3

import sys

import tspdata

n = int(sys.argv[1])
nsols = int(sys.argv[2])

a = tspdata.TSPData(n, [])
a.genrandom(n)

# a.savetofile('test.txt')
print('# n n_solutions')
print(n, nsols)
print('# n x n distance matrix')
print(a.matrixstring())
print('# set of given starting solutions')
for s in range(nsols):
    print(' '.join(str(x) for x in a.genrandomcycle()))
