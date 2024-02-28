from grammars import grammars
from cityGenerator import CityGenerator
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm
import numpy as np
from scipy.stats import kurtosis
from matplotlib.colors import ListedColormap
from matplotlib import colormaps
import random

random.seed(42)

# Create an instance of the CityGenerator class
cityGen = CityGenerator()

#G = cityGen.generateCity(30, grammars.Organic, seed=42, intersectRadius=0.5, showNodes=False, plotType=None, nodeLabelType="None")
#G = cityGen.generateCity(30, grammars.Grid, seed=42, intersectRadius=0.5, showNodes=False, plotType=None, nodeLabelType="None")
#G = cityGen.generateCity(30, grammars.Hex, seed=42, intersectRadius=0.5, showNodes=False, plotType=None, nodeLabelType="None")
G = cityGen.generateCity(50, grammars.Line, seed=42, intersectRadius=0.5, showNodes=False, plotType=None, nodeLabelType="None")

#each edge in G has an attribute called 'roadNumber', which is a unique identifier for each road. I want to calculate the betweenness centrality of each road, i.e how many of the shortest paths between pairs of nodes pass through a given road number

def calculateRoadBetweennessCentrality(G):
    # calculate the shortest path between each pair of nodes in the graph
    shortestPaths = dict(nx.all_pairs_shortest_path(G))
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
    # normalise the roadBetweenness values
    maxBetweenness = max(roadBetweenness.values())
    for roadNumber in roadBetweenness:
        roadBetweenness[roadNumber] /= maxBetweenness
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
    plt.colorbar(lc)
    plt.show()




# CALCULATING THE COMMUTING FLOW OF ROADS 
    
# Nodes of the graph G are expected to have an attribute demand that indicates how much flow a node wants to send 
# (negative demand) or receive (positive demand). Note that the sum of the demands should be 0 otherwise the problem 
# in not feasible.
# We will assume that this is modelling the 'morning commute', so residential nodes will have a negative demand,
# and commercial nodes will have a positive demand. This is because people will be travelling from residential areas to
# commercial areas in the morning.
    
# Nodes in G currently have a roadType attribute which is either m, l or s, for main, large or small road. We will assume
# that main nodes contain commercial building, large nodes contain half residential and half commercial buildings, and small
# nodes contain residential buildings.  
    
# Edges of the graph G are expected to have an attribute capacity that indicates how much flow the edge can support. 
# If this attribute is not present, the edge is considered to have infinite capacity. Default value: ‘capacity’.
# Since we have 3 types of road, main, large and small, we will assume that each of these has a different capacity, with
# main roads having the highest capacity, and small roads having the lowest capacity.
    
#print the nodes of G
#print(G.nodes(data=True))

#calculate the number of nodes in G that have a roadType of m, l or s
def assignDemands(G):
    mainNodes = [node for node in G.nodes(data=True) if node[1]['roadType'] == 'm']
    largeNodes = [node for node in G.nodes(data=True) if node[1]['roadType'] == 'l']
    smallNodes = [node for node in G.nodes(data=True) if node[1]['roadType'] == 's']
    noMainNodes = len(mainNodes)
    noLargeNodes = len(largeNodes)
    noSmallNodes = len(smallNodes)
    #calculate the LCM of noMainNodes and noSmallNodes
    def gcd(a, b):
        while b != 0:
            a, b = b, a % b
        return a
    def lcm(a, b):
        return a * b // gcd(a, b)
    lcmMainSmall = lcm(noMainNodes, noSmallNodes)
    mainDemands = lcmMainSmall/noMainNodes
    largeDemands = 0
    smallDemands = -lcmMainSmall/noSmallNodes
    #add an attribute to each node in G that represents the demand of that node
    for node in G.nodes(data=True):
        if node[1]['roadType'] == 'm':
            node[1]['demand'] = mainDemands
        elif node[1]['roadType'] == 'l':
            node[1]['demand'] = largeDemands
        elif node[1]['roadType'] == 's':
            node[1]['demand'] = smallDemands
    #print the sum of all demands
    print(sum([node[1]['demand'] for node in G.nodes(data=True)]))
            

def calculateFlows(G):
    assignDemands(G)
    # the capacity_scaling function only works with directed graphs, so we need to convert G to a directed graph. 
    # We will assume that the flow of traffic is unidirectional, so we will convert G to a directed graph by adding a
    # directed edge in both directions for each undirected edge in G. This assumes that there are no one way streets in the
    # city.
    G = nx.DiGraph(G.to_undirected())
    # print the edges of G
    #print(G.edges(data=True))

    flowCost, flowDict = nx.capacity_scaling(G)
    # If G is a digraph, a flowDict is a dict-of-dicts keyed by nodes such that flowDict[u][v] is the flow on edge (u, v).
    
    # add the flowDict to the edges of G, noting that flowDict is structured as a dict of dicts as described above
    for edge in G.edges():
        G.edges[edge]['flow'] = flowDict[edge[0]][edge[1]]
    # print the edges of G
    #print(G.edges(data=True))
        
    return flowCost, flowDict

def generateCommuteStartsandEnds(G):
    # create a list of all residents. Each small node will have 2 residents, and each large node will have 1 resident
    residents = []
    for node in G.nodes(data=True):
        if node[1]['roadType'] == 's':
            residents.append(node[0])
            residents.append(node[0])
        elif node[1]['roadType'] == 'l':
            residents.append(node[0])

    # create a list of all workplaces. Each main node will have 2 workplaces, and each large node will have 1 workplace
    workplaces = []
    for node in G.nodes(data=True):
        if node[1]['roadType'] == 'm':
            workplaces.append(node[0])
            workplaces.append(node[0])
        elif node[1]['roadType'] == 'l':
            workplaces.append(node[0])

    # If there are more workplaces than residents, add extra residents to the small nodes
    while len(residents) < len(workplaces):
        small_nodes = [node for node in G.nodes(data=True) if node[1]['roadType'] == 's']
        if small_nodes:
            node = random.choice(small_nodes)
            residents.append(node[0])
            if len(residents) >= len(workplaces):
                break

    # If there are more residents than workplaces, add extra workplaces to the main nodes
    while len(residents) > len(workplaces):
        main_nodes = [node for node in G.nodes(data=True) if node[1]['roadType'] == 'm']
        if main_nodes:
            node = random.choice(main_nodes)
            workplaces.append(node[0])
            if len(residents) <= len(workplaces):
                break

    #randomly pair residents with workplaces, so that each resident has a workplace
    commuteStartsAndEnds = {}
    for resident in residents:
        workplace = random.choice(workplaces)
        commuteStartsAndEnds[resident] = workplace
        workplaces.remove(workplace)

    return commuteStartsAndEnds

def calculateCommuteRoutes(G):
    # Calculate the shortest paths between each resident and their workplace. This is their commute route.
    commuteStartsAndEnds = generateCommuteStartsandEnds(G)
    commuteRoutes = {}
    for resident, workplace in commuteStartsAndEnds.items():
        commuteRoutes[resident] = nx.shortest_path(G, resident, workplace)
    return commuteRoutes

def plotSingleCommute(G, resident):
    # Plot the entire graph G in black, with the commute route of the given resident in red
    commuteRoutes = calculateCommuteRoutes(G)
    pos = nx.get_node_attributes(G, 'pos')

    # Create separate edge lists for each weight
    edges_1 = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] == 1]
    edges_05 = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] == 0.5]
    edges_025 = [(u, v) for u, v, d in G.edges(data=True) if d['weight'] == 0.25]

    plt.figure()

    # Draw the edges with different thicknesses
    nx.draw_networkx_edges(G, pos, edgelist=edges_1, edge_color='black', width=3.0)
    nx.draw_networkx_edges(G, pos, edgelist=edges_05, edge_color='black', width=2.0)
    nx.draw_networkx_edges(G, pos, edgelist=edges_025, edge_color='black', width=1.0)

    # Draw the nodes
    #nx.draw_networkx_nodes(G, pos, node_color='black', node_size=10)

    # Highlight the commute route of the given resident
    #nx.draw_networkx_nodes(G, pos, nodelist=[resident], node_color='red', node_size=10)

    # if there is no commute route for the given resident, raise an error
    if resident not in commuteRoutes:
        raise ValueError("Resident does not exist")

    nx.draw_networkx_edges(G, pos, edgelist=[(commuteRoutes[resident][i], commuteRoutes[resident][i+1]) for i in range(len(commuteRoutes[resident])-1)], edge_color='red')

    plt.show()

def calculateEdgeQuantity(G):
    # calculate which edge has the most flow during the morning commute
    commuteRoutes = calculateCommuteRoutes(G)
    edgeQuantity = {}
    for resident, route in commuteRoutes.items():
        for i in range(len(route)-1):
            edge = (route[i], route[i+1])
            if edge not in edgeQuantity:
                edgeQuantity[edge] = 1
            else:
                edgeQuantity[edge] += 1
    return edgeQuantity

def plotEdgeQuantity(G):
    # plot a heatmap of the quantity of traffic on each road during the morning commute
    edgeQuantity = calculateEdgeQuantity(G)
    edgeList = list(G.edges())
    lines = []
    colours = []
    for i in range(len(edgeList)):
        edge = edgeList[i]
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        lines.append([(x1, y1), (x2, y2)])
        if edge in edgeQuantity:
            colours.append(edgeQuantity[edge])
        else:
            colours.append(0)
    lc = LineCollection(lines, cmap='plasma', norm=LogNorm())
    lc.set_array(np.array(colours))
    fig, ax = plt.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    plt.colorbar(lc)
    plt.show()

#plotEdgeQuantity(G)
plotRoadsByClusteredBetweennessCentrality(G)
    




    