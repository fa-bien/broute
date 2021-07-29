#!/usr/bin/env python

import numbers

import matplotlib.pyplot as plt

def isNumber(x):
    return isinstance(x, numbers.Number)

lineStyles = [ 'solid',
               (0, (8, 4)),
               'dotted',
               (0, (8, 4, 2, 2)),
               (0, (8, 4, 2, 2, 2, 2, 2, 2)),
               'dotted',
               'dashdot'
]
lineColours = [ '#ae3638', '#3b69ac', 'green', 'orange', 'purple', 'brown',
                'pink' ]

# 'methods' is a list of methods to compare
# 'instances' is a list of instances to use for that comparison
# 'results' is a dict where results[i][m] is the performance (to be minimised)
# of method m on instance i
def plotPerformanceProfile(methods, instances, results,
                           fName='perfprof.pdf', descriptions=None,
                           title=None, logscale=False, interactive=True,
                           verbose=False):
    if not descriptions:
        descriptions = methods
    bestPerf = {}
    for inst in instances:
        allPerfs = [ results[inst][met] for met in methods
                     if isNumber(results[inst][met]) ]
        if len(allPerfs) > 0:
            bestPerf[inst] = min( allPerfs )
    perfRatios = {}
    for met in methods:
        perfRatios[met] = [ results[inst][met] / bestPerf[inst]
                            for inst in instances
                            if isNumber(results[inst][met]) ]
    allSteps = {}
    for met in methods:
        sr = sorted(perfRatios[met])
        steps = []
        for a, (i, b) in zip(sr[:-1], enumerate(sr[1:])):
            if a != b:
                steps.append( (a, (i + 1.0) / len(bestPerf) ) )
        steps.append( (sr[-1], float(len(sr)) / len(bestPerf)) )
        allSteps[met] = steps
    # compute bound
    worstPerf = max( [ allSteps[met][-1][0] for met in methods ] )
    #
    if verbose:
        print('worst performance:', worstPerf)
        for met in methods:
            for inst in instances:
                if isNumber(results[inst][met]) and \
                   results[inst][met] / bestPerf[inst] == worstPerf:
                    print('\tmethod:', met, '\tinstance:', inst)
    # cosmetics
    fig = plt.figure(figsize=(10, 5))
    ax = plt.subplot()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.axis( [1, worstPerf + .005 * (worstPerf - 1), 0, 1.02] )
    ax.set_yticks( [ .1 * x for x in range(11) ] )
    ax.yaxis.grid(True, ls='dotted')
    if logscale:
        ax.set_xscale('log')
    if title:
        ax.set_title(title, fontsize=16)
    # axis labels
    ax.set_xlabel('Performance level (lower is better)', size=14)
    ax.set_ylabel('Ratio of instances solved', size=14)
    # now we plot all of it
    for (i, met), name in zip(enumerate(methods), descriptions):
        xs = [ x[0] for x in allSteps[met] ]
        ys = [ x[1] for x in allSteps[met] ]
        xs.append(worstPerf)
        if len(perfRatios[met]) == len(bestPerf):
            ys.append(1)
        else:
            ys.append(ys[-1])
        ax.plot( xs, ys, drawstyle='steps-post',
                 label=name,
                 linestyle=lineStyles[i],
                 # antialiased=False,
                 color=lineColours[i],
                 linewidth=2)
        leg = ax.legend(loc='lower right', borderaxespad=.5, fontsize=14,
                        handlelength=3
                        # numpoints=50
        )
        # leg = plt.legend()
        leg.set_draggable(True)
    if interactive:
        plt.show()
    fig.savefig(fName, bbox_inches='tight')
    if verbose or interactive:
        print('saved figure to', fName)

def showAllFigures():
    plt.show()
