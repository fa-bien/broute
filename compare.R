runs <- read.csv('allruns.csv')

library(ggplot2)

## # All runtimes in seconds
## pdf('language_comparison_absolute.pdf')
## ggplot(runs, aes(x=factor(n), y=CPU_2opt, fill=factor(language))) +
##     geom_boxplot() + labs(x="n", y="2-opt CPU (s)", fill="Language")
## dev.off()



# All runtimes as a ratio of C++ run time
library(dplyr)
runs <- arrange(runs, language, instance)
cpp <- filter(runs, language=='c++')
runs$reference <- cpp$CPU
runs$normalised <- runs$CPU_2opt / runs$reference

pdf('language_comparison_relative.pdf')
ggplot(runs, aes(x=factor(n), y=normalised, fill=factor(language))) +
    geom_boxplot() + labs(x="n", y="2-opt CPU (ratio of C++ CPU)",
                          fill="Language")
dev.off()
