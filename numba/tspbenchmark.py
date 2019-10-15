#!/usr/bin/env python3

import time
import sys
import os

import tspdata
import tspsolution

# load experimental data from file
def loadfromfile(fname):
    n = 0
    d = []
    tours = []
    with open(fname) as f:
        for line in f:
            line = line[:line.find('#')]
            tokens = line.split()
            if len(tokens) == 0:
                continue
            elif n == 0 and len(tokens) == 2:
                n, nsols = int(tokens[0]), int(tokens[1])
            elif len(d) < n:
                # read one line of distance matrix
                d.append([int(x) for x in tokens])
            elif len(tours) < nsols:
                # read one starting solution
                tours.append([int(x) for x in tokens])
    data = tspdata.TSPData(n, d)
    return data, [tspsolution.TSPSolution(data, x) for x in tours]

# Solve each starting solution with first improvement 2-opt
# return the CPU time spent
def benchmarkone(solutions):
    nimpr = 0
    total2opttime = 0
    for sol  in solutions:
        t1 = time.process_time()
        n = sol.two_opt()
        t2 = time.process_time()
        total2opttime += t2 - t1
        nimpr += n
    return nimpr, total2opttime

# benchmark all input data, dump outcome
def benchmarkmany(dirname):
    #print('#language,instance,n,nsolutions,creation_time,CPU_2opt')
    for fn in os.listdir(dirname):
        data, solutions = loadfromfile(os.path.join(dirname, fn))
        nimpr, t = benchmarkone(solutions)
        print(','.join( (os.path.basename(os.getcwd()),
                         os.path.basename(fn), str(data.n),
                         str(len(solutions)), str(nimpr), str(t))))
        
if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.stderr.write('USAGE: ' + sys.argv[0] + ' tsp_data_file_dir\n')
        sys.exit(9)
    else:
        t = benchmarkmany(sys.argv[1])
