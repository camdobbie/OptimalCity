import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from shapely.geometry import Polygon, MultiPolygon
from optimisationMetrics import alpha_shape, headTailBreaks, calculateRoadBetweennessCentrality
import pickle
import numpy as np
from matplotlib.collections import LineCollection


def plotCityBlackWithAlphaShape(G, alpha=0.05, showNodes = False, nodeLabelType = None, edgeLabelType = None, show=True, savePath=None):
    fig, ax = plt.subplots(figsize=(3,3))#figsize=(10, 10))  
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
    edge_widths = [1 if G[u][v]['weight'] == 1 else 0.8 if G[u][v]['weight'] == 0.5 else 0.5 for u, v in edges]

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
    plt.axis('off')  # Turn on the axes
    plt.grid(False)  # Add a grid
    if show:
        plt.show()
    if savePath:
        plt.savefig(savePath, bbox_inches='tight')

def plotCityBlack(G, showNodes = False, nodeLabelType = None, edgeLabelType = None, show = True, savePath = None):

    fig, ax = plt.subplots(figsize=(10, 10))  
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
    edge_widths = [1 if G[u][v]['weight'] == 1 else 0.8 if G[u][v]['weight'] == 0.5 else 0.5 for u, v in edges]

    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx_edges(G, pos, edge_color='black', width=edge_widths, ax=ax)  # Draw edges with outline
    if edgeLabelType == "Edge Weight":
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    if edgeLabelType == "Road Number":
        edge_labels = nx.get_edge_attributes(G, 'roadNumber')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    nx.draw_networkx_nodes(G, pos, node_size=node_size, ax=ax)

    if with_labels:
        nx.draw_networkx_labels(G, pos, labels=labels, ax=ax)
    plt.axis('off')  # Turn on the axes
    plt.grid(False)  # Add a grid
    if show:
        plt.show()
    if savePath:
        plt.savefig(savePath, bbox_inches='tight')

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

def plotRoadsByBetweennessCentrality(graph, betweennessLoadPath = None, show=True, savePath=None):

    G = graph

    if betweennessLoadPath:
        with open(betweennessLoadPath, 'rb') as f:
            roadBetweenness = pickle.load(f)
    else:
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

    if show:
        plt.show()
    if savePath:
        plt.savefig(savePath, bbox_inches='tight')

def plotRoadsByClusteredBetweennessCentrality(graph, betweennessLoadPath=None, savePath=None, show=True):
    
    G = graph

    if betweennessLoadPath:
        with open(betweennessLoadPath, 'rb') as f:
            roadBetweenness = pickle.load(f)
    else:
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
    if show:
        plt.show()
    if savePath:
        plt.savefig(savePath, bbox_inches='tight')