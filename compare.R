library(dplyr)
library(ggplot2)

all_runs <- read.csv('allruns.csv')

languages <- c('c++', 'c++98', 'c++-static', 'julia', 'rust',
               'java', 'java-static', 'python', 'numba', 'pypy')
languages  <- c('c++', 'c++-nested')

benchmarks <- c('2-opt', 'Or-opt')

for(bench in benchmarks) {
    runs <- subset(all_runs, (language %in% languages) & benchmark == bench)
    
    ## ## All runtimes in seconds
    ## pdf(paste0('language_comparison_absolute_', bench, '.pdf'))
    ## p  <- ggplot(runs, aes(x=factor(n), y=time, fill=factor(language))) +
    ##     geom_boxplot() + labs(x='n', y='CPU time (s)', fill='Language',
    ##                           title=paste('Absolute CPU time for', bench,
    ##                                       'benchmark'))
    ## print(p)
    ## dev.off()
    
    ## All runtimes as a ratio of C++ run time
    runs <- arrange(runs, language, instance)
    cpp <- filter(runs, language=='c++')
    runs$reference <- cpp$time
    runs$normalised <- runs$time / runs$reference
    
    pdf(paste0('language_comparison_relative_', bench, '.pdf'))
    p  <- ggplot(runs, aes(x=factor(n), y=normalised, fill=factor(language))) +
        geom_boxplot() + labs(x='n', y='CPU time (ratio of C++ CPU time)',
                              fill='Language',
                              title=paste('CPU time relative to C++ for', bench,
                                          'benchmark'))
    print(p)
    dev.off()
}
