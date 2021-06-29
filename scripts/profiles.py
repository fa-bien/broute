#!/usr/bin/env python3

import sys
import os

import performanceprofile as pp
from functools import reduce

def load_all_CSVs(dirname):
    all_data = {}
    instances = set()
    read = 0
    for fn in os.listdir(dirname):
        if fn.endswith('.csv'):
            read += 1
            keys = []
            with open(os.path.join(dirname, fn)) as f:
                for line in f:
                    if keys == []:
                        keys = line.rstrip().split(',')
                    else:
                        tmp = {}
                        for key, value in zip(keys, line.rstrip().split(',')):
                            tmp[key] = value
                        all_data[tmp['implementation'], tmp['language'],
                                 tmp['matrix'], tmp['benchmark'],
                                 tmp['instance']] = float(tmp['time'])
                        instances.add(tmp['instance'])
    return instances, all_data

def normalise_time(data):
    for key in data:
        impl, lang, mat, bench, inst = key
        if impl != 'c++14':
            data[key] /= data['c++14', 'C++14', 'flat', bench, inst]
    for key in data:
        impl, lang, mat, bench, inst = key
        if impl == 'c++14':
            data[key] = 1.0

def makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix='Performance', fileprefix=''):
    impls = reduce(lambda x, y: x+y, (x[1] for x in comps))
    results = { bench: {i:{} for i in instances } for bench in benchmarks }
    for key in data:
        impl, lang, mat, bench, inst = key
        if impl in impls and bench in benchmarks:
            results[bench][inst][impl] = data[key]
    for bench in benchmarks:
        for lang, methods, names in comps:
            title = titleprefix + ' (' + (lang + ', ' if lang != '' else '') + bench + ')'
            fName = fileprefix + lang + '-' + bench + '-perfprof.pdf'

            print(fName)
            
            pp.plotPerformanceProfile(methods, instances, results[bench],
                                      title=title,
                                      fName=fName,
                                      descriptions=names)

def make_profiles(instances, data):
    
    # Impact of using a flat matrix
    benchmarks = ('2-opt', 'Or-opt', 'lns')
    comps = [ ('C++14', ('c++14', 'c++14-nested-matrix'), ('Flat', 'Nested')),
              ('Java', ('java', 'java-nested-matrix'), ('Flat', 'Nested')),
              ('JavaScript', ('javascript', 'javascript-nested-matrix'),
               ('Flat', 'Nested')),
              ('Julia', ('julia-flat-matrix', 'julia-array'),
               ('Flat', 'Square')),
              # ('CPython', ('python-flat-matrix', 'python'), ('Flat', 'Nested')),
              # ('Pypy', ('pypy', 'pypy-nested-matrix'), ('Flat', 'Nested')),
              # ('Numba', ('numba-flat-matrix', 'numba'), ('Flat', 'Square')),
              # ('Numpy', ('numpy-flat-matrix', 'numpy'), ('Flat', 'Square')),
             ]
    titlep = 'CPU performance of matrix representation'
    filep = 'matrix-'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    
    # Impact of using static arrays
    benchmarks = ('2-opt', 'Or-opt')
    comps = [ ('C++14', ('c++14', 'c++14-static-arrays'),('Dynamic', 'Static')),
              ('Java', ('java', 'java-static-arrays'), ('Dynamic', 'Static')) ]
    titlep = 'CPU performance of array data structure'
    filep = 'array-'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    
    ## Comparison of Python implementation
    ## 2-Opt and Or-opt are enough to weed out CPython and Numpy
    benchmarks = ('2-opt', 'Or-opt')
    comps = [ ('', ('python', 'pypy', 'numpy', 'numba'),
               ('CPython', 'Pypy', 'Numpy', 'Numba')) ]
    titlep = 'CPU performance of Python implementations'
    filep = 'python_implementations'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    
    # Zoom in on Pypy vs Numba
    benchmarks = ('2-opt', 'Or-opt', 'maxflow')
    comps = [ ('', ('pypy', 'numba'), ('Pypy', 'Numba')) ]
    titlep = 'Pypy vs Numba'
    filep = 'pypy_vs_numba'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    
    ## A comparison of C++ implementations
    benchmarks = ('2-opt', 'Or-opt', 'lns', 'espprc', 'maxflow')
    comps = [ ('', ('c++14', 'c++98'), ('C++14', 'C++98')) ]
    titlep = 'C++14 vs C++98'
    filep = 'C++14_vs_C++98-'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    
    ## General cross-language comparison...
    benchmarks = ('2-opt', 'Or-opt', 'lns', 'maxflow', 'espprc-index')
    comps = [ ('', ('c++98', 'java', 'javascript', 'julia-flat-matrix',
                    'pypy', 'rust'),
               ('C++98', 'Java', 'JavaScript', 'Julia', 'Python', 'Rust')) ]
    titlep = 'General cross-language comparison'
    filep = 'cross_language'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    ## ... including espprc without Rust
    benchmarks = ('espprc',)
    comps = [ ('', ('c++98', 'java', 'javascript', 'julia-flat-matrix', 'pypy'),
               ('C++98', 'Java', 'JavaScript', 'Julia', 'Python')) ]
    titlep = 'General cross-language comparison'
    filep = 'cross_language'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)

    ## Cross-language comparison: fast languages
    benchmarks = ('2-opt', 'Or-opt', 'lns', 'maxflow', 'espprc-index')
    comps = [ ('', ('c++98', 'java', 'julia-flat-matrix', 'rust'),
               ('C++98', 'Java', 'Julia', 'Rust')) ]
    titlep = 'Cross-language comparison: "Fast" languages'
    filep = 'fast_languages'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    ## ... including espprc without Rust
    benchmarks = ('espprc',)
    comps = [ ('', ('c++98', 'java', 'julia-flat-matrix'),
               ('C++98', 'Java', 'Julia')) ]
    titlep = 'Cross-language comparison: "Fast" languages'
    filep = 'fast_languages'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    
    ## Cross-language comparison: interpreted languages
    benchmarks = ('2-opt', 'Or-opt', 'lns', 'maxflow', 'espprc')
    comps = [ ('', ('pypy', 'javascript'),
               ('Python', 'JavaScript')) ]
    titlep = 'Cross-language comparison: "Interpreted" languages'
    filep = 'interpreted_languages'
    makeperfprofs(instances, data, benchmarks, comps,
                  titleprefix=titlep, fileprefix=filep)
    
    ## Cross-platform comparison
    # Not yet clear what to do here!
    
def main():
    csv_dir = '.'
    if len(sys.argv) > 1:
        csv_dir = sys.argv[1]
    instances, data = load_all_CSVs(csv_dir)
    # normalise_time(data)
    make_profiles(instances, data)

if __name__ == '__main__':
    main()
