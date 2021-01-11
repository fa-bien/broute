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

# Solve each starting solution using a given benchmark
# return the CPU time spent
def benchmarkone(solutions, benchmarkname):
    if benchmarkname == '2-opt':
        bench = lambda x: x.two_opt()
    elif benchmarkname.lower() == 'lns':
        bench = lambda x: x.lns()
    elif benchmarkname == 'Or-opt':
        bench = lambda x: x.or_opt()
    elif benchmarkname == 'espprc':
        bench = lambda x: x.espprc()
    elif benchmarkname == 'espprc-index':
        bench = lambda x: x.espprc(index=True)
    elif benchmarkname == 'maxflow':
        bench = lambda x: x.maxflow()
    elif benchmarkname == 'maxflow-RTF':
        bench = lambda x: x.maxflow(algorithm='RTF')
    else:
        bench = lambda x: None
    #
    nimpr = 0
    totalcputime = 0.0
    for sol in solutions:
        t1 = time.process_time()
        n = bench(sol)
        t2 = time.process_time()
        totalcputime += t2 - t1
        nimpr += n
    return nimpr, totalcputime

# benchmark all input data, dump outcome
def benchmarkmany(dirname, benchmarkname='2-opt'):
    #print('language,version,CPU,system,benchmark,instance,n,nsolutions,nimprovements,time(s)')
    for fn in os.listdir(dirname):
        data, solutions = loadfromfile(os.path.join(dirname, fn))
        nimpr, t = benchmarkone(solutions, benchmarkname)
        print(','.join( (os.path.basename(os.getcwd()),
                         sys.implementation.name + ' ' + sys.version.split()[0],
                         benchmarkname,
                         os.path.basename(fn), str(data.n),
                         str(len(solutions)), str(nimpr), str(t))))

def main():
    if len(sys.argv) < 2:
        sys.stderr.write('USAGE: ' + sys.argv[0] + \
                         ' tsp_data_file_dir [benchmark]\n')
        sys.exit(9)
    else:
        benchmark = '2-opt' if len(sys.argv) == 2 else sys.argv[2]
        t = benchmarkmany(sys.argv[1], benchmark)
    
if __name__ == '__main__':
    main()
