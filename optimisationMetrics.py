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
from shapely.ops import cascaded_union
from shapely.geometry import MultiPolygon


random.seed(42)

def calculateRoadBetweennessCentrality(G):
    # calculate the shortest path between each pair of nodes in the graph
    print("Calculating shortest paths...")
    shortestPaths = dict(nx.all_pairs_shortest_path(G))
    print("Shortest paths calculated.")
    # create a dictionary of edges and the number of shortest paths that pass through each edge
    edgeBetweenness = {} 

    total_nodes = len(shortestPaths)
    for i, source in enumerate(shortestPaths, start=1):
        print(f"Processing node {i} of {total_nodes}")

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
    return roadBetweenness

def plotRoadsInOrder(G):
    # create a list of the edges in G
    edgeList = list(G.edges())
    # create a list to hold the lines
    lines = []
    # create a list to hold the colours of the lines
    colours = []
    # iterate through each edge in G
    for i in range(len(edgeList)):
        edge = edgeList[i]
        # get the x and y coordinates of the start and end nodes of the edge
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        # add the start and end coordinates to the lines list
        lines.append([(x1, y1), (x2, y2)])
        # get the roadNumber of the edge
        roadNumber = G.edges[edge]['roadNumber']
        # add the colour of the edge to the colours list
        colours.append(roadNumber)
    # create a LineCollection from the lines
    lc = LineCollection(lines, cmap='plasma')
    # set the colours of the lines
    lc.set_array(np.array(colours))
    # plot the lines
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    plt.colorbar(lc)
    plt.show()

def plotRoadsByBetweennessCentrality(G):
    # calculate the road betweenness centrality
    roadBetweenness = calculateRoadBetweennessCentrality(G)
    # create a list of the edges in G
    edgeList = list(G.edges())
    # create a list to hold the lines
    lines = []
    # create a list to hold the colours of the lines
    colours = []
    # iterate through each edge in G
    for i in range(len(edgeList)):
        edge = edgeList[i]
        # get the x and y coordinates of the start and end nodes of the edge
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        # add the start and end coordinates to the lines list
        lines.append([(x1, y1), (x2, y2)])
        # get the roadNumber of the edge
        roadNumber = G.edges[edge]['roadNumber']
        # get the betweenness centrality of the road
        betweenness = roadBetweenness[roadNumber]
        # add the betweenness centrality to the colours list
        colours.append(betweenness)
    # create a LineCollection from the lines
    lc = LineCollection(lines, cmap='plasma')
    # set the colours of the lines
    lc.set_array(np.array(colours))
    # plot the lines
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    plt.colorbar(lc)
    plt.show()

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

def plotRoadsByClusteredBetweennessCentrality(G):
    # calculate the road betweenness centrality
    roadBetweenness = calculateRoadBetweennessCentrality(G)
    # create a list of the edges in G
    edgeList = list(G.edges())
    # create a list to hold the lines
    lines = []
    # perform head/tail breaks on the roadBetweenness dictionary
    clusters = headTailBreaks(roadBetweenness)
    # create a list of the clusters
    clusterList = list(clusters)
    # create a list of the colours of the lines
    colours = []
    # iterate through each edge in G
    for i in range(len(edgeList)):
        edge = edgeList[i]
        # get the x and y coordinates of the start and end nodes of the edge
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        # add the start and end coordinates to the lines list
        lines.append([(x1, y1), (x2, y2)])
        # get the roadNumber of the edge
        roadNumber = G.edges[edge]['roadNumber']
        # iterate through each cluster in the clusterList
        for j in range(len(clusterList)):
            cluster = clusterList[j]
            # if the roadNumber is in the cluster
            if roadNumber in cluster:
                # add the index of the cluster to the colours list
                colours.append(j)
    # create a LineCollection from the lines
    lc = LineCollection(lines, cmap='plasma')
    # set the colours of the lines
    lc.set_array(np.array(colours))
    # plot the lines
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    ax.set_aspect('equal')
    plt.colorbar(lc)
    plt.show()

def plotRoadsByClusteredBetweennessCentralityWidths(G):
    # calculate the road betweenness centrality
    roadBetweenness = calculateRoadBetweennessCentrality(G)
    # create a list of the edges in G
    edgeList = list(G.edges())
    # create a list to hold the lines
    lines = []
    # perform head/tail breaks on the roadBetweenness dictionary
    clusters = headTailBreaks(roadBetweenness)
    # create a list of the clusters
    clusterList = list(clusters)
    # create a list of the colours of the lines
    colours = []
    # create a list of the linewidths of the lines
    linewidths = []
    # iterate through each edge in G
    for i in range(len(edgeList)):
        edge = edgeList[i]
        # get the x and y coordinates of the start and end nodes of the edge
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        # add the start and end coordinates to the lines list
        lines.append([(x1, y1), (x2, y2)])
        # get the roadNumber of the edge
        roadNumber = G.edges[edge]['roadNumber']
        # iterate through each cluster in the clusterList
        for j in range(len(clusterList)):
            cluster = clusterList[j]
            # if the roadNumber is in the cluster
            if roadNumber in cluster:
                # add the index of the cluster to the colours list
                colours.append(j)
                # add the centrality value to the linewidths list
                linewidths.append(3 ** roadBetweenness[roadNumber])

    # reverse things so that the highest betweenness centrality roads are plotted on top
    lines = lines[::-1]
    colours = colours[::-1]
    linewidths = linewidths[::-1]

    lc = LineCollection(lines, cmap='plasma', linewidths=linewidths)
    # set the colours of the lines
    lc.set_array(np.array(colours))
    # plot the lines
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    ax.set_aspect('equal')
    #plt.colorbar(lc)
    plt.show()

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

"""
def calculatePopulation(G):
    totalLength = calculateTotalRoadLength(G)
    return totalLength * 4000

def calculatePopulationDensity(G, maxWidth, maxHeight):
    population = calculatePopulation(G)
    maxWidth = maxWidth / 10
    maxHeight = maxHeight / 10
    print(f"Population density: {population/(maxWidth*maxHeight)} people per square km.")
    return population/(maxWidth*maxHeight)
"""

def calculatePopulation(G):
    totalLength = calculateTotalRoadLength(G)
    return round(totalLength * 67.68)


def calculateConvexHull(G):
    pos = nx.get_node_attributes(G, 'pos')
    posList = list(pos.values())
    hull = ConvexHull(posList)
    return hull

def calculateConvexHullArea(G):
    hull = calculateConvexHull(G)
    pos = nx.get_node_attributes(G, 'pos')
    hull_points = [pos[i] for i in hull.vertices]
    polygon = Polygon(hull_points)
    area = polygon.area
    return area

def calculateConvexHullPopulationDensity(G):
    population = calculatePopulation(G)
    area = calculateConvexHullArea(G)
    areaKm = area / 100
    print(f"Population density (calculated using the convex hull): {round(population/areaKm)} people per square km.")
    return round(population/areaKm)



def plotCityBlackWithConvexHull(G, showNodes = False, nodeLabelType = None, edgeLabelType = None):

    fig, ax = plt.subplots()  
    ax.set_aspect('equal')

    if showNodes:
        node_size = 10
    else:
        node_size = 0
    if nodeLabelType == "Node Type":
        with_labels = True
        labels=nx.get_node_attributes(G, 'nodeType')
    elif nodeLabelType == "Node Number":
        with_labels = True
        labels = {node: node for node in G.nodes()}
    elif nodeLabelType == "Road Type":
        with_labels = True
        labels=nx.get_node_attributes(G, 'roadType')
    else:
        with_labels = False
        labels=None

    edges = G.edges()
    edge_widths = [3 if G[u][v]['weight'] == 1 else 2 if G[u][v]['weight'] == 0.5 else 1 for u, v in edges]

    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx_edges(G, pos, edge_color='black', width=edge_widths, ax=ax)  # Draw edges with outline
    if edgeLabelType == "Edge Weight":
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    if edgeLabelType == "Road Number":
        edge_labels = nx.get_edge_attributes(G, 'roadNumber')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    nx.draw_networkx_nodes(G, pos, node_size=node_size, ax=ax)

    # Calculate the convex hull
    hull = calculateConvexHull(G)
    # Get the vertices of the convex hull
    hull_points = [pos[i] for i in hull.vertices]

    # Create a Polygon patch
    hull_patch = patches.Polygon(hull_points, fill=None, edgecolor='red')

    # Add the patch to the Axes
    ax.add_patch(hull_patch)

    if with_labels:
        nx.draw_networkx_labels(G, pos, labels=labels, ax=ax)
    plt.axis('on')  # Turn on the axes
    plt.grid(False)  # Add a grid
    plt.show()



def alpha_shape(G, alpha=0.05):
    """
    Compute the alpha shape (concave hull) of a set of points.
    @param G: NetworkX graph.
    @param alpha: alpha value to influence the gooeyness of the border. Smaller numbers
                  don't fall inward as much as larger numbers. Too large, and you lose detail.
    @return: list of (x,y) coordinates
    """
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
    return cascaded_union(triangles), edge_points

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

def plotCityBlackWithAlphaShape(G, alpha=0.05, showNodes = False, nodeLabelType = None, edgeLabelType = None):
    fig, ax = plt.subplots()  
    ax.set_aspect('equal')

    if showNodes:
        node_size = 10
    else:
        node_size = 0
    if nodeLabelType == "Node Type":
        with_labels = True
        labels=nx.get_node_attributes(G, 'nodeType')
    elif nodeLabelType == "Node Number":
        with_labels = True
        labels = {node: node for node in G.nodes()}
    elif nodeLabelType == "Road Type":
        with_labels = True
        labels=nx.get_node_attributes(G, 'roadType')
    else:
        with_labels = False
        labels=None

    edges = G.edges()
    edge_widths = [3 if G[u][v]['weight'] == 1 else 2 if G[u][v]['weight'] == 0.5 else 1 for u, v in edges]

    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx_edges(G, pos, edge_color='black', width=edge_widths, ax=ax)  # Draw edges with outline
    if edgeLabelType == "Edge Weight":
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    if edgeLabelType == "Road Number":
        edge_labels = nx.get_edge_attributes(G, 'roadNumber')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    nx.draw_networkx_nodes(G, pos, node_size=node_size, ax=ax)

    # Calculate the alpha shape
    polygon, edge_points = alpha_shape(G, alpha)

    # Ensure the polygon is a MultiPolygon
    if isinstance(polygon, Polygon):
        polygon = MultiPolygon([polygon])

    # Iterate over each polygon in the MultiPolygon
    for poly in polygon.geoms:
        # Get the vertices of the alpha shape
        hull_points = list(poly.exterior.coords)

        # Create a Polygon patch
        hull_patch = patches.Polygon(hull_points, fill=None, edgecolor='red')

        # Add the patch to the Axes
        ax.add_patch(hull_patch)

    if with_labels:
        nx.draw_networkx_labels(G, pos, labels=labels, ax=ax)
    plt.axis('on')  # Turn on the axes
    plt.grid(False)  # Add a grid
    plt.show()