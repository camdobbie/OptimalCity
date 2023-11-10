import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import math
import random
import numpy as np

G = nx.Graph()


def calcIntersectionPoint(p1, p2, p3, p4): # Function to calculate the intersection point of two lines
    # first check if the lines do intersect
    if (p1[0] - p2[0])*(p3[1] - p4[1]) - (p1[1] - p2[1])*(p3[0] - p4[0]) == 0:
        return False
    else:
        # Calculate the intersection point
        x = ((p1[0]*p2[1] - p1[1]*p2[0])*(p3[0] - p4[0]) - (p1[0] - p2[0])*(p3[0]*p4[1] - p3[1]*p4[0])) / ((p1[0] - p2[0])*(p3[1] - p4[1]) - (p1[1] - p2[1])*(p3[0] - p4[0]))
        y = ((p1[0]*p2[1] - p1[1]*p2[0])*(p3[1] - p4[1]) - (p1[1] - p2[1])*(p3[0]*p4[1] - p3[1]*p4[0])) / ((p1[0] - p2[0])*(p3[1] - p4[1]) - (p1[1] - p2[1])*(p3[0] - p4[0]))
        # Check if the intersection point is at the endpoint of either line
        if (x == p1[0] and y == p1[1]) or (x == p2[0] and y == p2[1]) or (x == p3[0] and y == p3[1]) or (x == p4[0] and y == p4[1]):
            return False
        # check is the intersection point is on the line segments
        elif (x >= min(p1[0],p2[0]) and x <= max(p1[0],p2[0]) and y >= min(p1[1],p2[1]) and y <= max(p1[1],p2[1])) and (x >= min(p3[0],p4[0]) and x <= max(p3[0],p4[0]) and y >= min(p3[1],p4[1]) and y <= max(p3[1],p4[1])):
            return (x,y)
        else:
            return False


def createNodes(node,
                changeNodeTo,
                theta,
                length,
                newNodeType,
                weight = 1,
                useIntersectionRule=True,
                intersectRadius=None):
    """
    A function to create a new node and edge from an existing node
    
    node: the node to create the new node from
    changeNodeTo: the node type to change the current node to
    theta: the angle to rotate the incoming edge by
    length: the length of the new edge
    newNodeType: the type of the new node
    """

    newNode = list(G.nodes())[-1] + 1
    currentPosition = G.nodes[node]['pos']  # get the position of the current node
    currentDirection = G.nodes[node]['incEdge'] # get the direction of the incoming edge
    currentDirectionUnit = (currentDirection[0]/(currentDirection[0]**2 + currentDirection[1]**2)**0.5, currentDirection[1]/(currentDirection[0]**2 + currentDirection[1]**2)**0.5) # Normalise current direction into a unit vector
    currentDirectionRotated = (currentDirectionUnit[0] * math.cos(theta) - currentDirectionUnit[1] * math.sin(theta), currentDirectionUnit[0] * math.sin(theta) + currentDirectionUnit[1] * math.cos(theta)) # rotate the current direction by theta
    newDirection = (currentDirectionRotated[0] * length, currentDirectionRotated[1] * length) # scale the rotated direction by length
    newPosition = (currentPosition[0] + newDirection[0], currentPosition[1] + newDirection[1]) # calculate the new position

    
    # Check if the new edge intersects with any existing edge
    if useIntersectionRule:
        intersections = []
        for edge in G.edges():
            p1 = G.nodes[edge[0]]['pos']
            p2 = G.nodes[edge[1]]['pos']
            intersection = calcIntersectionPoint(p1, p2, currentPosition, newPosition)
            if intersection:  # If there is an intersection
                distance = ((intersection[0] - currentPosition[0])**2 + (intersection[1] - currentPosition[1])**2)**0.5
                intersections.append((intersection, distance))

        add_new_node = True

        if intersections:
            # Find the intersection with the smallest distance
            closest_intersection = min(intersections, key=lambda x: x[1])[0]

            # Check if the intersection point is too close to the parent node
            parent_position = G.nodes[node]['pos']
            distance_to_parent = ((closest_intersection[0] - parent_position[0])**2 + (closest_intersection[1] - parent_position[1])**2)**0.5
            if distance_to_parent < intersectRadius:
                add_new_node = False
            else:
                newPosition = closest_intersection

        # If add_new_node is False, return without adding the new node
        if not add_new_node:
            return

        # Check if the new node is closer to an existing node than intersectRadius
    if intersectRadius is not None:
        for existing_node in G.nodes():
            if existing_node == node:  # Skip the current node
                continue
            existing_position = G.nodes[existing_node]['pos']
            distance = ((newPosition[0] - existing_position[0])**2 + (newPosition[1] - existing_position[1])**2)**0.5
            if distance < intersectRadius:
                newNode = existing_node
                newPosition = existing_position
                break
    

    G.nodes[node]['nodeType'] = changeNodeTo # change the node type of the current node

    # if newPosition is already an existing node, then don't add a new node
    if newPosition in [G.nodes[i]['pos'] for i in G.nodes()]:
        G.add_edge(node, [G.nodes[i]['pos'] for i in G.nodes()].index(newPosition),weight=weight)
    else:
        G.add_node(newNode, nodeType=newNodeType, pos=newPosition, incEdge=newDirection) # add the new node to the graph
        G.add_edge(node, newNode,weight=weight) # add an edge between the new node and the old node


def productionRules1(node, useIntersectionRule, intersectRadius=None):
    if G.nodes[node]['nodeType'] == 'A':
        aAngle = random.uniform(0,2*math.pi)
        aLength = random.uniform(0.4,1.5)
        createNodes(node,'C',aAngle,aLength,'B', useIntersectionRule, intersectRadius)
    elif G.nodes[node]['nodeType'] == 'B':
        bAngle = random.uniform(0,2*math.pi)
        bLength = random.uniform(0.1,0.2)
        createNodes(node,'C',bAngle,bLength,'B', useIntersectionRule, intersectRadius)
        createNodes(node,'C',-bAngle,bLength,'B', useIntersectionRule, intersectRadius)

def productionRules2(node, useIntersectionRule, intersectRadius=None):
    if G.nodes[node]['nodeType'] == 'A':
        aAngle = random.uniform(1.5,1.6)
        aLength = random.uniform(0.4,1.5)
        createNodes(node,'C',aAngle,aLength,'B', useIntersectionRule, intersectRadius)
    elif G.nodes[node]['nodeType'] == 'B':
        bAngle = random.uniform(1.5,1.6)
        bLength = random.uniform(0.1,0.2)
        createNodes(node,'C',bAngle,bLength,'B', useIntersectionRule, intersectRadius)
        createNodes(node,'C',-bAngle,bLength,'B', useIntersectionRule, intersectRadius)

def productionRulesCity(node, useIntersectionRule, intersectRadius=None):
    if G.nodes[node]['nodeType'] == 'A':
        aAngle = math.pi/2
        aLength = 1
        createNodes(node,'mK',aAngle,aLength,'mL', useIntersectionRule=useIntersectionRule, intersectRadius=intersectRadius, weight=1)
        createNodes(node,'mK',-aAngle,aLength,'mL', useIntersectionRule=useIntersectionRule, intersectRadius=intersectRadius, weight=1)
    elif G.nodes[node]['nodeType'] == 'mL':
        aAngle = random.uniform(-0.1,0.1)
        aLength = 2
        createNodes(node,'mK',aAngle,aLength,'mL', useIntersectionRule=useIntersectionRule, intersectRadius=intersectRadius,weight=0.5)


production_rules = {
    'rule1': productionRules1,
    'rule2': productionRules2,
    'ruleCity': productionRulesCity
}

def generateCity(iterations, rule, useIntersectionRule=True, intersectRadius=None, seed=None, plotType="Map", showNodes = False, nodeLabelType = None, edgeLabelType = None):

    random.seed(seed)

    G.add_node(0, nodeType='A', pos=(0,0), incEdge=(0,1)) # incEdge is the direction of the incoming edge

    fig, ax = plt.subplots()

    def update(i):
        ax.clear()

        for node in list(G.nodes()):
            production_rules[rule](node, useIntersectionRule, intersectRadius)

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
        else:
            with_labels = False
            labels=None

        pos = nx.get_node_attributes(G, 'pos')
        nx.draw_networkx_edges(G, pos, edge_color='black', width=3.0, ax=ax)  # Draw edges with outline
        nx.draw_networkx_edges(G, pos, edge_color='#fafbdb', width=2.0, ax=ax)  # Draw edges
        if edgeLabelType == "Edge Weight":
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_size=node_size, ax=ax)

        if with_labels:
            nx.draw_networkx_labels(G, pos, labels=labels, ax=ax)
        plt.axis('on')  # Turn on the axes
        plt.grid(True)  # Add a grid

        """
        ax.set_xlim([-3.5, 0.5])  # Set x-axis limits
        ax.set_ylim([-2, 2])  # Set y-axis limits
        """

        # Add a text box displaying the current iteration
        iteration_text = f"Iteration: {i+1}/{iterations}"
        ax.text(0.02, 0.95, iteration_text, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    if plotType == "Animation":
        ani = animation.FuncAnimation(fig, update, frames=iterations, repeat=False)
        plt.show()
    else:
        for i in range(iterations):
            for node in list(G.nodes()):
                production_rules[rule](node, useIntersectionRule, intersectRadius)

        if plotType == "Map":
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
            else:
                with_labels = False
                labels=None

            edges = G.edges()
            # Create a list of colors based on the weights of the edges
            edge_colors = ['#fafbdb' if G[u][v]['weight'] == 1 else '#f7f6ee' for u, v in edges]

            pos = nx.get_node_attributes(G, 'pos')
            nx.draw_networkx_edges(G, pos, edge_color='black', width=3.0, ax=ax)  # Draw edges with outline
            nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2.0, ax=ax) 
            if edgeLabelType == "Edge Weight":
                edge_labels = nx.get_edge_attributes(G, 'weight')
                nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
            nx.draw_networkx_nodes(G, pos, node_size=node_size, ax=ax)

            if with_labels:
                nx.draw_networkx_labels(G, pos, labels=labels, ax=ax)

            plt.axis('on')  # Turn on the axes
            plt.grid(True)  # Add a grid

            plt.show()

    #return the graph object
    return G

#generateCity(10, 'rule1', useIntersectionRule=True,seed = 0,intersectRadius=0.1)
#G = generateCity(20, 'rule2', useIntersectionRule=True,seed = 1,intersectRadius=0.1,labelType="Node Number",plotType="Animation")
G = generateCity(20, 'ruleCity', useIntersectionRule=True,seed = 0,intersectRadius=0.1,edgeLabelType="Edge Weight",plotType="Map")


# dictionary of colours for each weight?
# at least start by labelling weights 