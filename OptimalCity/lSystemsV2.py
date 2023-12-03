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
        
def calculateNewPosition(G, node, theta, length):
    newNode = list(G.nodes())[-1] + 1
    currentPosition = G.nodes[node]['pos']  # get the position of the current node
    currentDirection = G.nodes[node]['incEdge'] # get the direction of the incoming edge
    currentDirectionUnit = (currentDirection[0]/(currentDirection[0]**2 + currentDirection[1]**2)**0.5, currentDirection[1]/(currentDirection[0]**2 + currentDirection[1]**2)**0.5) # Normalise current direction into a unit vector
    currentDirectionRotated = (currentDirectionUnit[0] * math.cos(theta) - currentDirectionUnit[1] * math.sin(theta), currentDirectionUnit[0] * math.sin(theta) + currentDirectionUnit[1] * math.cos(theta)) # rotate the current direction by theta
    newDirection = (currentDirectionRotated[0] * length, currentDirectionRotated[1] * length) # scale the rotated direction by length
    newPosition = (currentPosition[0] + newDirection[0], currentPosition[1] + newDirection[1]) # calculate the new position
    return newNode,newPosition

def checkProximity(G, position, intersectRadius):
    for existingNode in G.nodes():
        existingPosition = G.nodes[existingNode]['pos']
        distance = ((position[0] - existingPosition[0])**2 + (position[1] - existingPosition[1])**2)**0.5
        if distance < intersectRadius:
            return existingNode

def findClosestIntersection(G, node, newPosition):
    intersections = []
    currentPosition = G.nodes[node]['pos']
    for edge in G.edges():
        p1 = G.nodes[edge[0]]['pos']
        p2 = G.nodes[edge[1]]['pos']
        intersection = calcIntersectionPoint(p1, p2, currentPosition, newPosition)
        if intersection:  # If there is an intersection
            distance = ((intersection[0] - currentPosition[0])**2 + (intersection[1] - currentPosition[1])**2)**0.5
            intersections.append((intersection, distance))
    
    if intersections:
        closestIntersection = min(intersections, key=lambda x: x[1])[0]
        return closestIntersection
    else:
        return False
    
def calcMinDistanceToType(G, position, nodeType): # Calculate the minimum distance to a node of a certain type
    distance = math.inf
    if nodeType in nx.get_node_attributes(G, 'nodeType').values():
        for node in G.nodes():
            if G.nodes[node]['nodeType'] == nodeType:
                checkDistance = ((position[0] - G.nodes[node]['pos'][0])**2 + (position[1] - G.nodes[node]['pos'][1])**2)**0.5
                if checkDistance < distance:
                    distance = checkDistance
        return distance
    else:
        return math.inf
    
    
def checkBoundary(G, node, newPosition, width, height):
    currentPosition = G.nodes[node]['pos']

    boundaryIntersection = False

    # Check if the line intersects with the left boundary
    intersectionL = calcIntersectionPoint((-width/2, -height/2), (-width/2, height/2), currentPosition, newPosition)
    if intersectionL:
        boundaryIntersection = intersectionL

    # Check if the line intersects with the right boundary
    intersectionR = calcIntersectionPoint((width/2, -height/2), (width/2, height/2), currentPosition, newPosition)
    if intersectionR:
        boundaryIntersection = intersectionR

    # Check if the line intersects with the top boundary
    intersectionT = calcIntersectionPoint((-width/2, height/2), (width/2, height/2), currentPosition, newPosition)
    if intersectionT:
        boundaryIntersection = intersectionT

    # Check if the line intersects with the bottom boundary
    intersectionB = calcIntersectionPoint((-width/2, -height/2), (width/2, -height/2), currentPosition, newPosition)
    if intersectionB:
        boundaryIntersection = intersectionB

    if boundaryIntersection:
        return boundaryIntersection
    else:
        return False
    
def createNodes2(G, node, changeNodeTo, theta, length, newNodeType, weight = 1, width=None, height=None, intersectRadius=None):
    newNode,newPosition = calculateNewPosition(G, node, theta, length)
    # Check if the new edge intersects with any existing edge
    closestIntersection = findClosestIntersection(G, node, newPosition)
    if closestIntersection:
        newPosition = closestIntersection
        
    """ NOT CURRENTLY WORKING
    boundaryIntersection = checkBoundary(G, node, newPosition, width, height)
    
    if boundaryIntersection:
        newPosition = boundaryIntersection
        newNodeType = "boundary"
    """

    tooCloseNode = checkProximity(G, newPosition, intersectRadius)

    G.nodes[node]['nodeType'] = changeNodeTo # change the node type of the current node

    newDirection = (newPosition[0] - G.nodes[node]['pos'][0], newPosition[1] - G.nodes[node]['pos'][1]) # calculate the direction of the new edge

    if tooCloseNode:
        if node != tooCloseNode:
            G.add_edge(node, tooCloseNode,weight=weight)
    else:
        G.add_node(newNode, nodeType=newNodeType, pos=newPosition, incEdge=newDirection)
        G.add_edge(node, newNode,weight=weight)


def productionRulesCity(node, currentIteration, intersectRadius=None, width=None, height=None):

    if G.nodes[node]['nodeType'] == 'A':
        startingAngle = random.uniform(-math.pi,math.pi)
        length = 1
        createNodes2(G, node,'mT',startingAngle,length,'mL', intersectRadius=intersectRadius, weight=1, width=width, height=height)
        createNodes2(G, node,'mT',startingAngle + math.pi,length,'mL', intersectRadius=intersectRadius, weight=1, width=width, height=height)

    if G.nodes[node]['nodeType'] == 'mL':
        angle = random.uniform(-math.pi/10,math.pi/10)
        length = 1
        rng = random.random()
        newNode,newPosition = calculateNewPosition(G, node, angle, length)
        distanceTomBm = calcMinDistanceToType(G, newPosition, 'mBm')
        distanceTomBl = calcMinDistanceToType(G, newPosition, 'mBl')
        distanceToK = calcMinDistanceToType(G, newPosition, 'mK')
        distanceTolBm = calcMinDistanceToType(G, newPosition, 'lBm')
        distanceTolBl = calcMinDistanceToType(G, newPosition, 'lBl')
        distanceTolK = calcMinDistanceToType(G, newPosition, 'lK')
        if distanceTomBm > 12 and distanceToK > 12 and distanceTomBl > 12 and distanceTolBm > 7 and distanceTolBl > 7 and distanceTolK > 7:
            if rng < 0.2:
                createNodes2(G, node,'mBm',angle,length,'mL', intersectRadius=intersectRadius,weight=1, width=width, height=height)
            elif rng < 0.8:
                createNodes2(G, node,'mBl',angle,length,'mL', intersectRadius=intersectRadius,weight=1, width=width, height=height)
            else:
                createNodes2(G, node,'mT',angle,length,'mL', intersectRadius=intersectRadius,weight=1, width=width, height=height)
        else:
            createNodes2(G, node,'mT',angle,length,'mL', intersectRadius=intersectRadius,weight=1, width=width, height=height)
    
    if G.nodes[node]['nodeType'] == 'mBm':
        posNeg = random.choice([-1,1])
        angle = (math.pi/2) + random.uniform(-math.pi/10,math.pi/10)
        length = 1
        createNodes2(G, node,'mK',angle*posNeg,length,'mL', intersectRadius=intersectRadius, weight=1, width=width, height=height)
    
    if G.nodes[node]['nodeType'] == 'mBl':
        posNeg = random.choice([-1,1])
        angle = (math.pi/2) + random.uniform(-math.pi/10,math.pi/10)
        length = 1
        createNodes2(G, node,'mK',angle*posNeg,length,'lL', intersectRadius=intersectRadius, weight=0.5, width=width, height=height)

    if G.nodes[node]['nodeType'] == 'lL':
        angle = random.uniform(-math.pi/10,math.pi/10)
        length = 1
        rng = random.random()
        newNode,newPosition = calculateNewPosition(G, node, angle, length)
        createNodes2(G, node,'lT',angle,length,'lL', intersectRadius=intersectRadius, weight=0.5, width=width, height=height)
        distanceTomBm = calcMinDistanceToType(G, newPosition, 'mBm')
        distanceTomBl = calcMinDistanceToType(G, newPosition, 'mBl')
        distanceToK = calcMinDistanceToType(G, newPosition, 'mK')
        distanceTolBm = calcMinDistanceToType(G, newPosition, 'lBm')
        distanceTolBl = calcMinDistanceToType(G, newPosition, 'lBl')
        distanceTolK = calcMinDistanceToType(G, newPosition, 'lK')
        if distanceTomBm > 12 and distanceToK > 12 and distanceTomBl > 12 and distanceTolBm > 7 and distanceTolBl > 7 and distanceTolK > 7:
            if rng < 0.2:
                createNodes2(G, node,'lBl',angle,length,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)
            elif rng < 0.5:
                createNodes2(G, node,'lBs',angle,length,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)
            else:
                createNodes2(G, node,'lT',angle,length,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)
        else:
            createNodes2(G, node,'lT',angle,length,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)

    if G.nodes[node]['nodeType'] == 'lBl':
        posNeg = random.choice([-1,1])
        angle = (math.pi/2) + random.uniform(-math.pi/10,math.pi/10)
        length = 1
        createNodes2(G, node,'lK',angle*posNeg,length,'lL', intersectRadius=intersectRadius, weight=0.5, width=width, height=height)

    if G.nodes[node]['nodeType'] == 'lBs':
        posNeg = random.choice([-1,1])
        angle = (math.pi/2) + random.uniform(-math.pi/10,math.pi/10)
        length = 1
        createNodes2(G, node,'lK',angle*posNeg,length,'sL', intersectRadius=intersectRadius, weight=0.2, width=width, height=height)

    if G.nodes[node]['nodeType'] == 'sL':
        angle = random.uniform(1.5,1.6)
        length = 1
        createNodes2(G, node,'sT',angle,length,'sL', intersectRadius=intersectRadius, weight=0.2, width=width, height=height)
        createNodes2(G, node,'sT',-angle,length,'sL', intersectRadius=intersectRadius, weight=0.2, width=width, height=height)
       
def productionRulesCity2(node, currentIteration, intersectRadius=None, width=None, height=None):
    if G.nodes[node]['nodeType'] == 'A':
        aAngle = random.uniform(-math.pi,math.pi)
        aLength = random.uniform(7,10)
        createNodes2(G, node,'mT',aAngle,aLength,'mL', intersectRadius=intersectRadius, weight=1, width=width, height=height)
        createNodes2(G, node,'mT',aAngle + math.pi,aLength,'mL', intersectRadius=intersectRadius, weight=1, width=width, height=height)
    elif G.nodes[node]['nodeType'] == 'mL':

        singleAngle = random.uniform(-0.1,0.1)
        branchAngle = random.uniform(math.pi/3,math.pi/2)
        mLLength = random.uniform(5,8)
        rng = random.random()
        posNeg = random.choice([-1,1])
        #print(0.05-currentIteration/1000)
        #print(iterations)
    
        threshold = 0.2-currentIteration/100

        if rng < threshold:
            createNodes2(G, node,'mB',singleAngle,mLLength+5,'mL', intersectRadius=intersectRadius,weight=1, width=width, height=height)
            createNodes2(G, node,'mB',(branchAngle)**posNeg,mLLength+5,'mL', intersectRadius=intersectRadius,weight=1, width=width, height=height)

        else:
            createNodes2(G, node,'mT',singleAngle,mLLength,'mL', intersectRadius=intersectRadius,weight=1, width=width, height=height)

    elif G.nodes[node]['nodeType'] == 'mT':
        rng = random.random()
        branchAngle = random.uniform(1.2,1.8)
        posNeg = random.choice([-1,1])
        if rng < 0.3: # 50% chance of creating a new node
            createNodes2(G, node,'mK',branchAngle**posNeg,4,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)
        else:
            G.nodes[node]['nodeType'] = 'mK'

    elif G.nodes[node]['nodeType'] == 'lL':
        rng1 = random.random()
        rng2 = random.random()
        threshold = 0.2-currentIteration/100
        posNeg = random.choice([-1,1])
        bAngle = random.uniform(1.5,1.6)
        singleAngle = random.uniform(-0.1,0.1)
        bLength = random.uniform(3,4)
        createNodes2(G, node,'lT',singleAngle,bLength,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)
        if rng1 < threshold:
            createNodes2(G, node,'lT',bAngle**posNeg,bLength,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)

        #createNodes(node,'lT',-bAngle,bLength,'lL', intersectRadius=intersectRadius,weight=0.5, width=width, height=height)

production_rules = {
    'ruleCity': productionRulesCity,
    'ruleCity2': productionRulesCity2
}

def generateCity(iterations, rule, width=None, height=None, intersectRadius=None, seed=None, plotType="Map", showNodes = False, nodeLabelType = None, edgeLabelType = None):

    random.seed(seed)

    G.add_node(0, nodeType='A', pos=(0,0), incEdge=(0,1)) # incEdge is the direction of the incoming edge

    fig, ax = plt.subplots()

    def graphSettings():
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
        edge_colors = ['#ffd747' if G[u][v]['weight'] == 1 else '#e3e3e3' if G[u][v]['weight'] == 0.5 else '#dbdbdb' for u, v in edges]
        edge_widths = [4 if G[u][v]['weight'] == 1 else 3 if G[u][v]['weight'] == 0.5 else 2 for u, v in edges]
        edge_widthsBlack = [x + 1 for x in edge_widths]

        pos = nx.get_node_attributes(G, 'pos')
        nx.draw_networkx_edges(G, pos, edge_color='black', width=edge_widthsBlack, ax=ax)  # Draw edges with outline
        nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, ax=ax)  # Draw edges
        if edgeLabelType == "Edge Weight":
            edge_labels = nx.get_edge_attributes(G, 'weight')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)
        nx.draw_networkx_nodes(G, pos, node_size=node_size, ax=ax)

        if with_labels:
            nx.draw_networkx_labels(G, pos, labels=labels, ax=ax)
        plt.axis('on')  # Turn on the axes
        plt.grid(True)  # Add a grid

    def update(i):
        print(f"Starting iteration: {i+1}/{iterations}")
        ax.clear()

        for node in list(G.nodes()):
            production_rules[rule](node, i+1, intersectRadius, width, height)

        graphSettings()

        """
        ax.set_xlim([-70, 70])  # Set x-axis limits
        ax.set_ylim([-70, 70])  # Set y-axis limits
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
            print(f"Starting iteration: {i+1}/{iterations}")
            for node in list(G.nodes()):
                production_rules[rule](node, i, intersectRadius, width, height)

        if plotType == "Map":
            graphSettings()
            plt.show()

    #return the graph object
    return G

#G = generateCity(100, 'ruleCity2', intersectRadius=1.5, seed=3, showNodes=False, plotType="Map",nodeLabelType=None, width=120, height=120)
G = generateCity(50, 'ruleCity', intersectRadius=0.9, seed=0, showNodes=False, plotType="Map",nodeLabelType=None, width=120, height=120)
