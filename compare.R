all_runs <- read.csv('prev.csv')

## runs <- subset(all_runs, !(language %in% c('c++', 'python', 'java'
##                                            ## 'numba', 'pypy', 'java',
##                                            ## 'java-static'
##                                            )))
runs <- subset(all_runs, (language %in% c('c++', 'java', 'rust', 'julia'
                                          ## 'numba', 'pypy', 'java',
                                          ## 'java-static'
                                          )))

library(ggplot2)

# All runtimes in seconds
pdf('language_comparison_absolute.pdf')
ggplot(runs, aes(x=factor(n), y=time, fill=factor(language))) +
    geom_boxplot() + labs(x="n", y="CPU time (s)", fill="Language")
dev.off()



# All runtimes as a ratio of C++ run time
library(dplyr)
runs <- arrange(runs, language, instance)
cpp <- filter(runs, language=='c++')
runs$reference <- cpp$time
runs$normalised <- runs$time / runs$reference

pdf('language_comparison_relative.pdf')
ggplot(runs, aes(x=factor(n), y=normalised, fill=factor(language))) +
    geom_boxplot() + labs(x="n", y="CPU time (ratio of C++ CPU time)",
                          fill="Language")
dev.off()
