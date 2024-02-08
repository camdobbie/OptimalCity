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

# Create an instance of the CityGenerator class
cityGen = CityGenerator()

G = cityGen.generateCity(30, grammars.Organic, seed=42, intersectRadius=0.5, showNodes=False, plotType=None, nodeLabelType="None")

def calculateBetweennessAverageCentrality(G):
    centralityDict = nx.betweenness_centrality(G)
    averageCentrality = sum(centralityDict.values())/len(centralityDict)
    return averageCentrality

# when generateCity is created, the graph is plotted but not shown. I want to overlay a heatmap of the betweenness centrality of each node on top of the graph
# I want to use the betweenness centrality of each node to determine the colour of the node in the heatmap

def plotHeatmapNodes(G):
    # Create a dictionary of node centrality values
    centralityDict = nx.betweenness_centrality(G)
    # Create a list of the centrality values
    centralityList = list(centralityDict.values())
    # Create a list of the nodes in the graph
    nodeList = list(G.nodes())
    # Create a list of the x and y coordinates of the nodes
    xList = [G.nodes[node]['pos'][0] for node in nodeList]
    yList = [G.nodes[node]['pos'][1] for node in nodeList]
    # Create a scatter plot of the nodes, with the colour of the nodes determined by the centrality of the node
    plt.scatter(xList, yList, c=centralityList, cmap='plasma', s=100, alpha=0.5)
    plt.colorbar()
    plt.show()

# do the same but plot the betweenness centrality of the edges
def plotHeatmapEdges(G):
    # Create a dictionary of edge centrality values
    centralityDict = nx.edge_betweenness_centrality(G)
    # Create a list of the centrality values
    centralityList = list(centralityDict.values())
    # Convert centralityList to a NumPy array
    centralityArray = np.array(centralityList)
    # Create a list of the edges in the graph
    edgeList = list(G.edges())
    # Create a list to hold the lines
    lines = []
    # Plot a line of each edge, with the colour of the edge determined by the centrality of the edge
    for i in range(len(edgeList)):
        edge = edgeList[i]
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        lines.append([(x1, y1), (x2, y2)])
    # Create a LineCollection from the lines
    lc = LineCollection(lines, array=centralityArray, cmap='plasma', alpha=0.5, norm=LogNorm())
    # Add the LineCollection to the plot
    plt.gca().add_collection(lc)
    # Set the limits of the plot to the minimum and maximum x and y values of the nodes in the graph
    plt.xlim(min([G.nodes[node]['pos'][0] for node in G.nodes()])*1.2, max([G.nodes[node]['pos'][0] for node in G.nodes()])*1.2)
    plt.ylim(min([G.nodes[node]['pos'][1] for node in G.nodes()])*1.2, max([G.nodes[node]['pos'][1] for node in G.nodes()])*1.2)


    # Create a colorbar
    plt.colorbar(lc)
    plt.show()

def singleHeadTailBreak(data):
    #perform head/tail breaks on the data, and output a list of the parts

    #sort the data
    data.sort()
    #calculate the mean
    mean = sum(data)/len(data)
    #split the data on either side of the mean
    head = [x for x in data if x <= mean]
    tail = [x for x in data if x > mean]
    return head, tail

def headTailBreaks(data, edgeCentralityDict, G, maxClusters=None, clusters=None, counter=0):
    if clusters is None:
        clusters = []

    if maxClusters is not None and counter == maxClusters:
        return clusters

    if len(data) <= 1:
        for i, cluster in enumerate(clusters):
            for centrality in cluster:
                for edge, edgeCentrality in edgeCentralityDict.items():
                    if edgeCentrality == centrality:
                        start_node_pos = G.nodes[edge[0]]['pos']
                        end_node_pos = G.nodes[edge[1]]['pos']
                        print(f"Cluster: {i+1}, Centrality: {centrality}, Edge: {edge}, Start Position: {start_node_pos}, End Position: {end_node_pos}")
        return clusters

    head, tail = singleHeadTailBreak(data)
    clusters.append(head)
    return headTailBreaks(tail, edgeCentralityDict, G, maxClusters, clusters, counter+1)

def plotClusteredHeatmapEdges(G, maxClusters=None):
    # Create a dictionary of edge centrality values
    centralityDict = nx.edge_betweenness_centrality(G)
    # Create a list of the centrality values
    centralityList = list(centralityDict.values())
    # Create a dictionary of edges and their corresponding centrality values
    edgeCentralityDict = {edge: centrality for edge, centrality in zip(G.edges(), centralityList)}
    # Cluster the centrality values
    clusters = headTailBreaks(centralityList, edgeCentralityDict, G, maxClusters)
    # Create a dictionary that maps each edge to its cluster number
    edgeClusterDict = {edge: next((j for j, cluster in enumerate(clusters) if centrality in cluster), 0) for edge, centrality in edgeCentralityDict.items()}
    # Create a list of the edges in the graph
    edgeList = list(G.edges())
    # Create a list to hold the lines
    lines = []
    # Create a list to hold the colors
    colors = []
    # Plot a line of each edge, with the color of the edge determined by the cluster of the centrality of the edge
    for edge in edgeList:
        x1 = G.nodes[edge[0]]['pos'][0]
        y1 = G.nodes[edge[0]]['pos'][1]
        x2 = G.nodes[edge[1]]['pos'][0]
        y2 = G.nodes[edge[1]]['pos'][1]
        lines.append([(x1, y1), (x2, y2)])
        # Find the cluster of the edge and use it as the color
        color = edgeClusterDict[edge]
        colors.append(color)
    # Generate a list of colors
    cmap = colormaps.get_cmap('plasma')
    color_list = [cmap(i/(max(colors)+1)) for i in range(max(colors)+1)]

    # Create a LineCollection from the lines
    lc = LineCollection(lines, array=colors, cmap=ListedColormap(color_list), alpha=0.5,)
    # Add the LineCollection to the plot
    plt.gca().add_collection(lc)
    # Set the limits of the plot to the minimum and maximum x and y values of the nodes in the graph
    plt.xlim(min([G.nodes[node]['pos'][0] for node in G.nodes()])*1.2, max([G.nodes[node]['pos'][0] for node in G.nodes()])*1.2)
    plt.ylim(min([G.nodes[node]['pos'][1] for node in G.nodes()])*1.2, max([G.nodes[node]['pos'][1] for node in G.nodes()])*1.2)
    # Create a colorbar
    plt.colorbar(lc)
    plt.show()

#plotHeatmapEdges(G)
#plotClusteredHeatmapEdges(G)
plotClusteredHeatmapEdges(G, maxClusters=5)