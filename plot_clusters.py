import numpy
import matplotlib.pyplot as plot


##############################################################################
# functions for plotting the data and printing to console

# epsilon parameter: the radius to draw circles around plotted objects from clusters and noise
def plotData(clusters, noise, epsilon, axisSize, xLabel, yLabel):
    print "noise of size", len(noise)

    for object in noise:
        plot.plot(object[0], object[1], 'o', markersize=5, markerfacecolor="black")
        drawCircle(object[0], object[1], epsilon)
        print object
    print

    colors = plot.cm.Spectral(numpy.linspace(0, 1, len(clusters)))

    for index, cluster in enumerate(clusters):
        print "cluster", index + 1, "of size", len(cluster)

        for object in cluster:
            plot.plot(object[0], object[1], 'o', markersize=12, markerfacecolor=colors[index])
            drawCircle(object[0], object[1], epsilon)
            print object
        print

    plot.axis([0, axisSize, 0, axisSize])
    plot.xlabel(xLabel)
    plot.ylabel(yLabel)
    plot.show()

def drawCircle(x, y, radius):
    circle = plot.Circle((x, y), radius, color='black', linewidth=0.1, fill=False)
    plot.gca().add_patch(circle)