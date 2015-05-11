import sys
sys.path.append(".\isclust")
import isclust
sys.path.append(".")
import dbscan as dm
import plot_clusters as plot
import timeit

##############################################################################
# Main execution segment

# DBSCAN parameters
epsilon = 0.6
minimumObjects = 4

# switch to use generated data or own data
useGeneratedData = True

if useGeneratedData:
    # generate sample data
    sigma = 0.5
    NumPoints = 20
    db1 = isclust.genDataXY(NumPoints, sigma, 2, 2)  # return a list of lists. Each list [label, x0, x1,....]
    db2 = isclust.genDataXY(NumPoints, sigma, 6, 6)
    db3 = isclust.genDataXY(NumPoints, sigma, 2, 6)
    data = db1 + db2 + db3
    # remove the initial label attribute from each object in the list: [label, x0, x1] -> [x0, x1]
    for i in data:
        i.pop(0)
    # parameters for plotting the data
    xLabel = "x axis"
    yLabel = "y axis"
    axisSize = 10

# get data from file
else:
    # retrieve data
    data = [[]]  # TODO
    # parameters for plotting the data
    xLabel = "TODO"
    yLabel = "TODO"
    axisSize = 1


# get execution times of DBSCAN with and without grid indexing optimization, each timing test is run 10 times
unoptimizedTime = timeit.timeit("dbscan.dbscan(data, epsilon, minimumObjects)",
                    setup="import dbscan; from __main__ import data, epsilon, minimumObjects", number=10)
optimizedTime = timeit.timeit("dbscan.dbscan(data, epsilon, minimumObjects, True)",
                    setup="import dbscan; from __main__ import data, epsilon, minimumObjects", number=10)

print "unoptimizedTime      ", unoptimizedTime, ";      optimizedTime", optimizedTime
print "optimization factor  ", unoptimizedTime / optimizedTime
print

# plot the results
clusters, noise = dm.dbscan(data, epsilon, minimumObjects, True)
plot.plotData(clusters, noise, epsilon, axisSize, xLabel, yLabel)