#!/usr/bin/env Rscript

library(dplyr)
library(ggplot2)

## reference implementation for ratio calculation
refimpl <- 'c++14'
csvdir <- 'csv/Xeon'

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

## we isolate CPU times of referenec implementation
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
                                   'julia-flat-matrix', 'julia-square-matrix'))

for (benchmark in c("2-opt", "Or-opt")) {
    for (n in c(20, 40, 60)) {
        pdf(paste0('impact_flat_matrix-', benchmark, '-', n, '.pdf'))
        title <- paste0('Relative CPU effort per language depending on matrix representation\n(', benchmark, ', ', n, ' cities)')
        p <- ggplot(subset(ds, n == 20 & benchmark == benchmark),
                    aes(x=language, y=normalised, fill=matrix)) +
            geom_boxplot() + labs(x='Language',
                                  y='CPU time (ratio of C++14 time)',
                                  fill='Matrix representation',
                                  title=title)
        print(p)
        dev.off()
    }
}
