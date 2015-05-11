# Algorithm
#
# DBSCAN(data, k)
#   Arbitrary select a point p with label Unknown
#   If p is a border point (non-core point), label it as NOISE:
#      no points are density-reachable from p and DBSCAN visits the next point of the database.
#   If p is a core point, a cluster is formed by
#      Retrieving all points density-reachable (dr) from p w.r.t. Eps and MinPts:
#   retrieve all ddr points from p, retrieve all ddr points of the ddr points,
#   Labeling all retrieved points with the cluster label.
#   Merge the current cluster to existing cluster if find any dr point that is already a member of a cluster
#   Continue the process until all of the points have been processed.
#
import sys
sys.path.append(".\isclust")

import math
import msvcrt
import isclust
import random
import time
import sets

# Cluster data
# data: a list of objects. Each object is a list. The first attribute is the cluster label
#


def dbscan(data, Eps, MinPts, gnuplot):
  grid = divideDataInGrid(data, Eps)

  clusters = []
  clusterId = 1

  isclust.plotDBSCAN(gnuplot, data, clusters, "X", "Y", 0, 10, 0, 10, "DBSCAN")
  if( isclust.checkKey() ):
    return []

  while(1):
    for p in data:
      cluster,mergeList = findAllDrs(clusterId, p, data, Eps, MinPts, grid)
      if( len(cluster) > 0 ):
        # Merge cluster
        mergedCluster = cluster
        mergeList = sets.Set(mergeList)
        for cid in mergeList:
          mergedCluster += clusters[cid-1]
          for d in clusters[cid-1]:
            d[0] = clusterId
          clusters[cid-1] = []

        # append the current cluster to the cluster set
        clusters.append(mergedCluster)
        clusterId += 1

        isclust.plotDBSCAN(gnuplot, data, clusters, "X", "Y", 0, 10, 0, 10, "DBSCAN")
        if( isclust.checkKey() ):
          return []

    if( isclust.checkKey() ):
      return []

  return clusters

# Find all density reachable points from a core point p
def findAllDrs(clusterId, p, data, Eps, MinPts, grid):
  if( p[0] > 0 ): # already assigned
    return [],[]

  ddrs,mergeList = findAllDdrs(clusterId, p, data, Eps, MinPts)
  #print "ddrs", ddrs
  ddrs2 = []
  for q in ddrs:
    d,m = findAllDrs(clusterId, q, getNeighbors(data, grid, q, Eps), Eps, MinPts, grid)
    ddrs += d
    mergeList += m
  return ddrs, mergeList

# find all directly density reachable points from a core point p
def findAllDdrs(clusterId, p, data, Eps, MinPts):
  ddrs = []
  mergeList = []
  NptsNo = 0

  # check if p is a core point
  for i in data:
    if(i is p):
      continue
    distance = isclust.disimilarity(p,i)
    if( distance < Eps ):
      NptsNo += 1
      ddrs.append(i)

  if( NptsNo >= MinPts ): # core point
    cluster = []
    p[0] = clusterId
    for j in ddrs:
      if( j[0] <= 0):  #
        j[0] = clusterId
        cluster.append(j)
      else:
        mergeList.append(j[0])
    return cluster,mergeList
  else:
    return [],[]

def getNeighbors(data, grid, point, epsilon):
    neighbors = []
    firstDimension = calculateGridInex(point[1], epsilon)
    secondDimension = calculateGridInex(point[2], epsilon)

    neighbors += grid[firstDimension - 1][secondDimension - 1]
    neighbors += grid[firstDimension - 1][secondDimension]
    neighbors += grid[firstDimension - 1][secondDimension + 1]
    neighbors += grid[firstDimension][secondDimension - 1]
    neighbors += grid[firstDimension][secondDimension]
    neighbors += grid[firstDimension][secondDimension + 1]
    neighbors += grid[firstDimension + 1][secondDimension - 1]
    neighbors += grid[firstDimension + 1][secondDimension]
    neighbors += grid[firstDimension + 1][secondDimension + 1]

    return data

def calculateGridInex(value, epsilon):
    return int(value * 1/epsilon)  # get floor value

# use for grid indexing
def divideDataInGrid(data, epsilon):
    gridSize = int(10 / epsilon)  # get floor value, as integer for index usage
    grid = [[[] for x in range(gridSize)] for x in range(gridSize)]

    for obj in data:
        firstDimension = calculateGridInex(obj[1], epsilon)
        secondDimension = calculateGridInex(obj[2], epsilon)
        grid[firstDimension][secondDimension].append(obj)

    return grid

if __name__ == '__main__':
  gnuplot = isclust.getGnuPlot()
  time.sleep(1)

  sigma = 0.5
  NumPoints = 20
  db1 = isclust.genDataXY(NumPoints, sigma, 2, 2)  # return a list of lists. Each list [label, x0, x1,....]
  db2 = isclust.genDataXY(NumPoints, sigma, 6, 6)
  db3 = isclust.genDataXY(NumPoints, sigma, 2, 6)
  db = db1 + db2 + db3
  #data = [[0,1,1], [0,1, 2], [0,1,1.5], [0, 5, 4], [0, 4.5, 4], [0, 4, 4.8]]

  Eps = 1.5
  MinPts = 5
  centroids = dbscan(db, Eps, MinPts, gnuplot)

  import timeit
  print(timeit.timeit("dbscan(db, Eps, MinPts, gnuplot)", setup="from __main__ import test"))

  #Eps = 3
  #MinPts = 5
  # centroids = dbscan(db, Eps, MinPts, gnuplot)

