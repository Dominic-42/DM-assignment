import math


##############################################################################
# functions for DBSCAN clustering

# data parameter: list of 2 item lists (features) to be clustered
# returns: clusters, noise
def dbscan(data, epsilon, minimumObjects, useOptimization = False):
    UNASSIGNED_LABEL = -1   # label for objects that haven't been assigned to a cluster or marked as noise
    NOISE_LABEL = 0         # label for noise objects
    clusterLabel = 0        # label for objects of a cluster, the label will be incremented for each new clusters

    labeledObjects = [[UNASSIGNED_LABEL] + i for i in data]  # the first attribute of each object represents
    #                                                          which label the object is assigned to

    indexingGrid = divideDataInGrid(labeledObjects, epsilon) if useOptimization else None

    for labelObject in labeledObjects:
        if labelObject[0] != UNASSIGNED_LABEL:
            continue

        #                 directly density reachable
        neighborObjects = optimizedRetrieveNeighbors(labeledObjects, indexingGrid, labelObject, epsilon)

        if len(neighborObjects) < minimumObjects:
            labelObject[0] = NOISE_LABEL
        else:
            # get new cluster
            clusterLabel += 1
            labelObject[0] = clusterLabel  # initial object from which a cluster is created and starts expanding if possible
            unassignedObjects = neighborObjects  # objects that haven't been handled yet

            # assigned all neighbors (directly density reachable) to cluster
            for neighborObject in neighborObjects:
                neighborObject[0] = clusterLabel

            # look for rest of density reachable objects
            while not len(unassignedObjects) == 0:
                labelObject = unassignedObjects.pop()
                neighborObjects = optimizedRetrieveNeighbors(labeledObjects, indexingGrid, labelObject, epsilon)

                if len(neighborObjects) >= minimumObjects:
                    for neighborObjects in neighborObjects:
                        if neighborObjects[0] <= 0:  # not in a cluster
                            neighborObjects[0] = clusterLabel
                            unassignedObjects.append(neighborObjects)

    return getClusters(data, labeledObjects, clusterLabel, NOISE_LABEL)

# assign data to clusters or noise list according to their labels
# return: clusters and noise list
def getClusters(data, labeledObjects, clusterNumber, NOISE_LABEL):
    clusters = [[] for i in range(clusterNumber)]
    noise = []
    for i, object in enumerate(labeledObjects):
        if object[0] == NOISE_LABEL:
            noise.append(data[i])
        else:
            clusters[object[0] - 1].append(data[i])

    return clusters, noise

# retrieve all neighbors within a radius around a object
def retrieveNeighbors(labeledObjects, labelObject, radius):
    neighbors = []

    for potentialNeighbor in labeledObjects:
        if labelObject == potentialNeighbor:
            continue
        if euclideanDistance(labelObject[1:3], potentialNeighbor[1:3]) <= radius:
            neighbors.append(potentialNeighbor)

    return neighbors

def euclideanDistance(object1, object2):
    x1 = object1[0]
    y1 = object1[1]
    x2 = object2[0]
    y2 = object2[1]

    return math.sqrt((x1-x2)**2 + (y1-y2)**2)


##############################################################################
# functions for optimization:
# pre index the data into grids and get objects from surrounding grid cells of the cell an object is in
# to reduce the number of potential neighbors the DBSCAN has to search for

def getPotentialNeighbors(grid, labelObject, epsilon):
    potentialNeighbors = []
    xIndex = calculateGridIndex(labelObject[1], epsilon)
    yIndex = calculateGridIndex(labelObject[2], epsilon)
    gridBoundary = len(grid)

    # get surrounding grid cells
    for x in range(xIndex - 1, xIndex + 2):
        for y in range(yIndex - 1, yIndex + 2):
            if x in range(gridBoundary) and y in range(gridBoundary):
                potentialNeighbors += (grid[x][y])

    return potentialNeighbors

def calculateGridIndex(value, epsilon):
    return int(value * 1/epsilon)  # get floor value

# use for grid indexing
# return: grid, 2 dimensional list
def divideDataInGrid(labeledObjects, epsilon):
    gridSize = int(10 / epsilon)  # get floor value, as integer for index usage
    grid = [[[] for x in range(gridSize)] for x in range(gridSize)]

    for labelObject in labeledObjects:
        x = calculateGridIndex(labelObject[1], epsilon)
        y = calculateGridIndex(labelObject[2], epsilon)
        grid[x][y].append(labelObject)

    return grid

def optimizedRetrieveNeighbors(labeledObjects, grid, labelObject, radius):
    if grid is not None:
        labeledObjects = getPotentialNeighbors(grid, labelObject, radius)

    return retrieveNeighbors(labeledObjects, labelObject, radius)
