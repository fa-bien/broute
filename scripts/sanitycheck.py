#!/usr/bin/env python3

import sys

REF_IMPL = 'c++14'

def loadCSV(fnames):
    out = {}
    for fname in fnames:
        lines = []
        with open(fname, 'r') as f:
            lines = f.readlines()
        # read and process header...
        columns = lines[0].rstrip().split(',')
        column_index = { col: index
                         for (index, col) in enumerate(columns) }
        # now actually read rows of experimental data
        for line in lines[1:]:
            tokens = line.rstrip().split(',')
            impl = tokens[column_index['implementation']]
            bench = tokens[column_index['benchmark']]
            instance = tokens[column_index['instance']]
            checksum = tokens[column_index['checksum']]
            out[impl, bench, instance] = checksum
    return out

# return true if expdata contains only checksum-consistent results across
# different languages, false otherwise
def sanityCheck(expdata):
    allgood = True
    for impl, bench, inst in expdata:
        # we could pick any language but c++ is likely to be in all data sets
        if impl != REF_IMPL:
            if expdata[impl, bench, inst] != expdata[REF_IMPL, bench, inst]:
                print('Inconsistent data between', REF_IMPL, 'and', impl,
                      'for benchmark', bench, 'and instance',
                      inst, ':', expdata[REF_IMPL, bench, inst], 'vs',
                      expdata[impl, bench, inst])
                allgood = False
    return allgood

def main():
    fnames = ['allruns.csv']
    if len(sys.argv) > 1:
        fnames = sys.argv[1:]
    expdata = loadCSV(fnames)
    sane = sanityCheck(expdata)
    if sane:
        print('CSV files contain consistent data across languages')
    else:
        print('Inconsistent data found in CSV files')
        
if __name__ == '__main__':
    main()
