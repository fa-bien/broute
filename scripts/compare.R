#!/usr/bin/env Rscript

library(dplyr)
library(ggplot2)
library(colorspace)

colours <- c("#2571ac", "#cb6528", "#c37ea3", "#000000", "#f0ed60", "#3c9975")
palette <- scale_color_manual(values=colours)

lines <- element_line(size=.3)
mytheme <- theme(axis.text.x=element_blank(),
                 axis.ticks.x = element_blank(),
                 panel.grid.major.x = element_blank(),
                 panel.grid.minor.x = element_blank(),
                 panel.grid.major.y = lines,
                 panel.grid.minor.y = lines)

## reference implementation for ratio calculation
refimpl <- 'c++14'

## result directory as first command line argument
args = commandArgs(trailingOnly=TRUE)
csvdir <- ifelse(length(args) ==0, 'results/ryzen_5_3600', args[1])

## first we glue all data together in one data frame
fnames <- list.files(path=csvdir, pattern='*.csv')

all_runs <- read.csv(paste0(csvdir, '/', fnames[1]))
for(fn in fnames[2:length(fnames)]) {
    tmp <- read.csv(paste0(csvdir, '/', fn))
    all_runs <- rbind(all_runs, tmp)
}

for (col in c('implementation', 'language', 'matrix', 'version',
              'benchmark', 'instance')) {
    all_runs[,col] <- factor(all_runs[,col])
}

## we isolate CPU times of reference implementation
refdata <- filter(all_runs, implementation==refimpl)
refdata$reftime <- refdata$time
normalised <- left_join(all_runs, refdata,
                        by=c('benchmark', 'instance', 'checksum'))
## We take this opportunity to check checksum consistency
if (nrow(all_runs) != nrow(normalised)) {
    print('Error: checksum inconsistency')
    quit(save='no')
}
## now create a new data frame with normalised times
runs <- arrange(all_runs, implementation, benchmark, instance)
normtmp <- arrange(normalised, implementation.x, benchmark, instance)
runs$reftime <- normtmp$reftime
runs$normalised <- runs$time / runs$reftime

## Now we can generate charts

## distance matrix representation comparison
ds <- subset(runs,
             implementation %in% c('c++14', 'c++14-nested-matrix',
                                   'java', 'java-nested-matrix',
                                   'javascript', 'javascript-nested-matrix',
                                   'julia-flat-matrix', 'julia-array'))
for (lang in c('C++14', 'Java', 'JavaScript', 'Julia')) {
    for (bench in c('2-opt', 'Or-opt', 'lns')) {
        pdf(paste0('matrix-', lang, '-', bench, '-boxplot.pdf'))
        title <- paste0(lang, ': relative CPU effort of matrix representations (', bench, ')')
        p <- ggplot(subset(ds, language == lang & benchmark == bench),
                    aes(y=normalised, colour=matrix, fill=after_scale(color))) +
            facet_wrap(~n, strip.position="bottom") + 
            geom_boxplot(alpha=0.2, outlier.alpha=.5) +
            labs(x='n', y='CPU time (ratio of C++14 time)',
                 title=title, color='Matrix\nrepresentation') +
            theme_bw() + mytheme + palette
        print(p)
        dev.off()
    }
}

## Impact of using static arrays
ds <- subset(runs, implementation %in% c('c++14', 'c++14-static-arrays',
                                         'java', 'java-static-arrays'))
for (lang in c('C++14', 'Java')) {
    for (bench in c('2-opt', 'Or-opt')) {
        pdf(paste0('array-', lang, '-', bench, '-boxplot.pdf'))
        title <- paste0(lang, ': relative CPU effort of array type\n(',
                        bench, ')')
        p <- ggplot(subset(ds, language == lang & benchmark == bench),
                    aes(y=normalised,
                        color=implementation, fill=after_scale(color))) +
            facet_wrap(~n, strip.position="bottom") + 
            geom_boxplot(alpha=0.2, outlier.alpha=.5) +
            labs(x='n', y='CPU time (ratio of C++14 time)',
                 color='Implementation', title=title) +
            theme_bw() + mytheme + palette
        print(p)
        dev.off()
    }
}

## A comparison of Python implementations
## Flat vs Nested matrix depending on Python interpreter
ds <- subset(runs, implementation %in% c('python', 'python-flat-matrix',
                                         'pypy', 'pypy-nested-matrix',
                                         'numpy', 'numpy-flat-matrix',
                                         'numba', 'numba-flat-matrix'))
ds$impl <- as.character(ds$implementation)
ds <- ds %>% mutate(interpreter = factor(
                        case_when(
                            startsWith(impl, 'pypy') ~ 'Pypy',
                            startsWith(impl, 'numba') ~ 'Numba',
                            startsWith(impl, 'numpy') ~ 'Numpy',
                            TRUE ~ 'CPython'),
                        levels=c('CPython','Pypy','Numpy','Numba')))

for (bench in c('2-opt', 'Or-opt')) {
    for (inter in c('CPython', 'Pypy', 'Numba', 'Numpy')) {
        pdf(paste0('matrix-', inter, '-', bench, '-boxplot.pdf'))
        title <- paste0(inter,
                        ': relative CPU effort of matrix representation (', bench, ')')
        p <- ggplot(subset(ds, interpreter == inter & benchmark == bench),
                    aes(y=normalised, color=matrix, fill=after_scale(color))) +
            facet_wrap(~n, strip.position="bottom") + 
            geom_boxplot(alpha=0.2, outlier.alpha=.5) +
            labs(x='n', y='CPU time (ratio of C++14 time)',
                 color='Matrix\nrepresentation', title=title) +
            theme_bw() + mytheme + palette
        print(p)
        dev.off()
    }
}

## performance of Python interpreters
pythonbest <- subset(ds,
                     implementation %in% c('python', 'pypy', 'numpy', 'numba'))
for (bench in c('2-opt', 'Or-opt', 'lns', 'espprc', 'maxflow')) {
    title <-paste0('Relative CPU effort of Python implementations (', bench,')')
    pdf(paste0('python_implementations-', bench, '-boxplot.pdf'))
    p <- ggplot(subset(pythonbest, benchmark == bench),
                aes(y=normalised,
                    color=interpreter, fill=after_scale(color))) +
        facet_wrap(~n, strip.position="bottom") + 
        geom_boxplot(alpha=0.2, outlier.alpha=.5) +
        labs(x='n', y='CPU time (ratio of C++14 time)', title=title,
             color='Implementation') +
        theme_bw() + mytheme + palette
    print(p)
    dev.off()
}

for (bench in c('2-opt', 'Or-opt', 'maxflow')) {
    title <- paste0('Pypy vs Numba (', bench, ')')
    pdf(paste0('pypy_vs_numba-', bench, '-boxplot.pdf'))
    p <- ggplot(subset(pythonbest, benchmark == bench &
                       interpreter %in% c('Pypy', 'Numba')),
                aes(y=normalised,
                    color=factor(interpreter,), fill=after_scale(color))) +
        facet_wrap(~n, strip.position="bottom") + 
        geom_boxplot(alpha=0.2, outlier.alpha=.5) +
        labs(x='n', y='CPU time (ratio of C++14 time)',
             color='Implementation', title=title) +
        theme_bw() + mytheme + palette
    print(p)
    dev.off()
}

## A comparison of C++ implementations
ds <- subset(runs, implementation %in% c('c++14', 'c++98'))
for (bench in c('2-opt', 'Or-opt', 'lns', 'espprc', 'maxflow')) {
    pdf(paste0('C++14_vs_C++98-', bench, '-boxplot.pdf'))
    title <- paste0('C++14 vs C++98 (', bench, ')')
    p <- ggplot(subset(ds, benchmark == bench),
                aes(y=normalised, color=language, fill=after_scale(color))) +
        facet_wrap(~n, strip.position="bottom") + 
        geom_boxplot(alpha=0.2, outlier.alpha=.5) +
        labs(x='n', y='CPU time (ratio of C++14 time)',
             color='Language', title=title) +
        theme_bw() + mytheme + palette
    print(p)
    dev.off()
}

## ## General cross-language comparison
## ds <- subset(runs, implementation %in%
##                    c('c++98', 'java', 'javascript', 'julia-flat-matrix',
##                      'pypy', 'rust'))
## for (bench in c('2-opt', 'Or-opt', 'lns', 'espprc', 'espprc-index', 'maxflow')){
##     pdf(paste0('cross_language-', bench, '-boxplot.pdf'))
##     title <- paste0('General cross-language comparison (', bench, ')')
##     p <- ggplot(subset(ds, benchmark == bench),
##                 aes(y=normalised, color=language, fill=after_scale(color))) +
##         facet_wrap(~n, strip.position="bottom") + 
##         geom_boxplot(alpha=0.2, outlier.alpha=.5) +
##         labs(x='n', y='CPU time (ratio of C++14 time)',
##              color='Language', title=title) + 
##         theme_bw() + mytheme + palette
##     print(p)
##     dev.off()
## }

## Cross-language comparison: fast languages
ds <- subset(runs, implementation %in%
                   c('c++98', 'java', 'julia-flat-matrix', 'rust'))
for (bench in c('2-opt', 'Or-opt', 'lns', 'espprc', 'espprc-index', 'maxflow')){
    pdf(paste0('fast_languages-', bench, '-boxplot.pdf'))
    title <- paste0('Relative performance of "fast" languages (', bench, ')')
    p <- ggplot(subset(ds, benchmark == bench),
                aes(y=normalised, color=language, fill=after_scale(color))) +
        facet_wrap(~n, strip.position="bottom") + 
        geom_boxplot(alpha=0.2, outlier.alpha=.5) +
        labs(x='n', y='CPU time (ratio of C++14 time)',
             color='Language', title=title) +
        theme_bw() + mytheme + palette
    print(p)
    dev.off()
}

## Cross-language comparison: interpreted languages
ds <- subset(runs, implementation %in%
                   c('pypy', 'javascript'))
for (bench in c('2-opt', 'Or-opt', 'lns', 'espprc', 'maxflow')){
    pdf(paste0('interpreted_languages-', bench, '-boxplot.pdf'))
    title <- paste0('Relative performance of "interpreted" languages (',
                    bench, ')')
    p <- ggplot(subset(ds, benchmark == bench),
                aes(y=normalised, color=language, fill=after_scale(color))) +
        facet_wrap(~n, strip.position="bottom") + 
        geom_boxplot(alpha=0.2, outlier.alpha=.5) +
        labs(x='n', y='CPU time (ratio of C++14 time)',
             color='Language', title=title) + 
        theme_bw() + mytheme + palette
    print(p)
    dev.off()
}







## end of currently used plots

## ## Cross-platform comparison
## ## not clear what to do here - maybe just mention cases where different platforms yield different results?



## ## FAILED EXPERIMENT might work well with less outliers but as things are now,
## ##                   a bit hard to read
## ## ## distance matrix representation comparison
## ## ds <- subset(runs,
## ##              implementation %in% c('c++14', 'c++14-nested-matrix',
## ##                                    'java', 'java-nested-matrix',
## ##                                    'javascript', 'javascript-nested-matrix',
## ##                                    'julia-flat-matrix', 'julia-array'))
## ## for (bench in c('2-opt', 'Or-opt')) {
## ##     pdf(paste0('matrix-', bench, '-boxplot.pdf'))
## ##     title <- paste0('Relative CPU effort with matrix representation (', bench, ')')
## ##     p <- ggplot(subset(ds, benchmark == bench),
## ##                 aes(x=factor(n), y=normalised, fill=matrix)) +
## ##         facet_wrap(~language, scales='free_y') +
## ##         geom_boxplot() + labs(x='n',
## ##                               y='CPU time (ratio of C++14 time)',
## ##                               fill='matrix representation',
## ##                               title=title)
## ##     print(p)
## ##     dev.off()
## ## }
