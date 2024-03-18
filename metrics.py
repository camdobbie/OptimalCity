from grammars import grammars
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm
import numpy as np
from scipy.stats import kurtosis
from matplotlib.colors import ListedColormap
from matplotlib import colormaps
import random
from scipy.spatial import ConvexHull
from matplotlib.patches import Polygon
from scipy.spatial import Delaunay
from shapely.geometry import GeometryCollection, Polygon, MultiLineString
from shapely.ops import unary_union, polygonize
from shapely import geometry
import matplotlib.patches as patches
from scipy.spatial import Delaunay
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely.geometry import MultiPolygon
from tqdm import tqdm
import pickle


def calculateShortestPaths(G, shortestPathsSavePath=None):
    # calculate the shortest path between each pair of nodes in the graph
    shortestPaths = {}
    for source in G.nodes():
        print(f"Calculating shortest paths from node {source} of {len(G.nodes())}")
        shortestPaths[source] = nx.single_source_shortest_path(G, source)


    if shortestPathsSavePath:
        with open(shortestPathsSavePath, 'wb') as f:
            pickle.dump(shortestPaths, f)

    return shortestPaths

def calculateRoadBetweennessCentrality(G, shortestPathsSavePath=None, betweennessSavePath=None):

    shortestPaths = calculateShortestPaths(G, shortestPathsSavePath)

    # create a dictionary of edges and the number of shortest paths that pass through each edge
    edgeBetweenness = {} 

    for i, source in enumerate(tqdm(shortestPaths, desc="Processing nodes"), start=1):
        for target in shortestPaths[source]:
            # if the source and target are different nodes
            if source != target:
                # get the shortest path between the source and target nodes
                path = shortestPaths[source][target]
                # iterate through each edge in the path
                for i in range(len(path)-1):
                    # get the edge
                    edge = (path[i], path[i+1])
                    # if the edge is not in the dictionary, add it
                    if edge not in edgeBetweenness:
                        edgeBetweenness[edge] = 1
                    # if the edge is in the dictionary, increment the value
                    else:
                        edgeBetweenness[edge] += 1
    # for each possible roadNumber, calculate how many shortest paths pass through that road
    roadNumbers = set(nx.get_edge_attributes(G, 'roadNumber').values())
    roadBetweenness = {}
    for roadNumber in roadNumbers:
        roadBetweenness[roadNumber] = 0
        for edge in edgeBetweenness:
            if G.edges[edge]['roadNumber'] == roadNumber:
                roadBetweenness[roadNumber] += edgeBetweenness[edge]

    # normalise the roadBetweenness values using min-max normalisation
    maxBetweenness = max(roadBetweenness.values())
    minBetweenness = min(roadBetweenness.values())
    for roadNumber in roadBetweenness:
        roadBetweenness[roadNumber] = (roadBetweenness[roadNumber] - minBetweenness) / (maxBetweenness - minBetweenness)

    if betweennessSavePath:
        with open(betweennessSavePath, 'wb') as f:
            pickle.dump(roadBetweenness, f)

    return roadBetweenness

def calculateAverageCircuity(G,shortestPathsLoadPath):
    #average circuity is defined as the mean of all circuity values for each pair of nodes in the graph.
    # for each pair of nodes, circuity is the shortest path length divided by the euclidean distance between the nodes
    with open(shortestPathsLoadPath, 'rb') as f:
        shortestPaths = pickle.load(f)
    circuityList = []
    for source in tqdm(shortestPaths, desc="Calculating circuity"):
        for target in shortestPaths[source]:
            if source != target:
                path = shortestPaths[source][target]
                shortestPathLength = len(path) - 1
                x1 = G.nodes[source]['pos'][0]
                y1 = G.nodes[source]['pos'][1]
                x2 = G.nodes[target]['pos'][0]
                y2 = G.nodes[target]['pos'][1]
                euclideanDistance = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
                circuity = shortestPathLength / euclideanDistance
                circuityList.append(circuity)
    averageCircuity = sum(circuityList) / len(circuityList)
    return averageCircuity



def singleHeadTailBreak(roadCentralityDict):
    #sort the dictionary by value in descending order
    sortedDict = dict(sorted(roadCentralityDict.items(), key=lambda item: item[1]))
    #calculate the mean value
    mean = sum(sortedDict.values())/len(sortedDict)
    #split roadCentralityDict on either side of the mean
    head = {k: v for k, v in sortedDict.items() if v >= mean}
    tail = {k: v for k, v in sortedDict.items() if v < mean}
    return tail, head

def headTailBreaks(roadCentralityDict, clusters = None, counter = 0):
    """function to perform head/tail breaks on the data, and output a list of the parts.
    the clusters parameter is used to pass the clusters list between recursive calls of the function
    the output is a list of dictionaries, each containing the roadNumbers and betweenness centrality values of the roads in that cluster"""
    if clusters is None:
        clusters = []
    #if there is only one road in the dictionary, add it to the clusters list and return the list
    if len(roadCentralityDict) == 1:
        clusters.append(roadCentralityDict)
        return clusters
    #if there are two roads in the dictionary, split the dictionary into two parts and add them to the clusters list
    elif len(roadCentralityDict) == 2:
        tail, head = singleHeadTailBreak(roadCentralityDict)
        clusters.append(tail)
        clusters.append(head)
        return clusters
    #if there are more than two roads in the dictionary, split the dictionary into two parts and call the function again on each part
    else:
        tail, head = singleHeadTailBreak(roadCentralityDict)
        clusters.append(tail)
        return headTailBreaks(head, clusters, counter+1)



def calculateTotalRoadLength(G):
    totalLength = 0
    for edge in G.edges():
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        totalLength += length
    return totalLength
    
def calculateRoadDensity(G, maxWidth, maxHeight):
    totalLength = calculateTotalRoadLength(G)
    return totalLength/(maxWidth*maxHeight)


def calculatePopulation(G):
    totalLength = calculateTotalRoadLength(G)
    return round(totalLength * 154.15)#67.68)

def alpha_shape(G, alpha=0.05):

    # Get the positions of the nodes
    pos = nx.get_node_attributes(G, 'pos')

    # Convert the positions to a list of points
    points = [Point(p) for p in pos.values()]

    if len(points) < 4:
        # When you have a triangle, there is no sense in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull

    coords = np.array([point.coords[0] for point in points])
    tri = Delaunay(coords)
    triangles = coords[tri.vertices]
    a = ((triangles[:,0,0] - triangles[:,1,0]) ** 2 + (triangles[:,0,1] - triangles[:,1,1]) ** 2) ** 0.5
    b = ((triangles[:,1,0] - triangles[:,2,0]) ** 2 + (triangles[:,1,1] - triangles[:,2,1]) ** 2) ** 0.5
    c = ((triangles[:,2,0] - triangles[:,0,0]) ** 2 + (triangles[:,2,1] - triangles[:,0,1]) ** 2) ** 0.5
    s = ( a + b + c ) / 2.0
    areas = (s*(s-a)*(s-b)*(s-c)) ** 0.5
    circums = a * b * c / (4.0 * areas)
    filtered = triangles[circums < (1.0 / alpha)]
    edge1 = filtered[:,(0,1)]
    edge2 = filtered[:,(1,2)]
    edge3 = filtered[:,(2,0)]
    edge_points = np.unique(np.concatenate((edge1,edge2,edge3)), axis = 0).tolist()
    m = geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))
    return unary_union(triangles), edge_points

def calculateAlphaShapeArea(G, alpha=0.05):
    polygon, edge_points = alpha_shape(G, alpha)
    area = polygon.area
    return area

def calculateAlphaShapePopulationDensity(G, alpha=0.05):
    population = calculatePopulation(G)
    area = calculateAlphaShapeArea(G, alpha)
    areaKm = area / 100
    print(f"Population density (calculated using the alpha shape): {round(population/areaKm)} people per square km.")
    return round(population/areaKm)
