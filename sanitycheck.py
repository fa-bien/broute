#!/usr/bin/env python3

import sys

def loadCSV(fname):
    out = {}
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
        lang = tokens[column_index['language']]
        bench = tokens[column_index['benchmark']]
        instance = tokens[column_index['instance']]
        checksum = tokens[column_index['checksum']]
        out[lang, bench, instance] = checksum
    return out

# return true if expdata contains only checksum-consistent results across
# different languages, false otherwise
def sanityCheck(expdata):
    allgood = True
    for lang, bench, inst in expdata:
        # c++ provides reference values
        # we could pick any language but c++ is likely to be in all data sets
        if lang != 'c++':
            if expdata[lang, bench, inst] != expdata['c++', bench, inst]:
                print('Inconsistent data between c++ and', lang,
                      'for benchmark', bench, 'and instance',
                      inst, ':', expdata['c++', bench, inst], 'vs',
                      expdata[lang, bench, inst])
                allgood = False
    return allgood

def main():
    fname = 'allruns.csv'
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    expdata = loadCSV(fname)
    sane = sanityCheck(expdata)
    if sane:
        print('CSV file contains consistent data across languages')
    else:
        print('Inconsistent data found in CSV file')
        
if __name__ == '__main__':
    main()
