import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import math
import random
import numpy as np

counter = 0
creationCalcs = 0
updateCalcs = 0

seed = 3
random.seed(seed)
np.random.seed(seed)

G = nx.Graph()

roadTypes = ["m","l","s"]
nodeTypesGen = ["K","T","B","L"]
#make nodeRoadsAndTypes a list of all possible combinations of roadTypes and nodeTypesGen
nodeRoadsAndTypes = [roadType + nodeType for roadType in roadTypes for nodeType in nodeTypesGen]



def get_random_theta(minimum,maximum):
    theta = random.uniform(minimum,maximum)*random.choice([-1,1])
    return theta

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

    if nodeType in nodeRoadsAndTypes:
        for node in G.nodes():
            if G.nodes[node]['roadType'] + G.nodes[node]['nodeType']== nodeType:
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
    
def createNodes(G, node, changeNodeTo, theta, length, newRoadType, newNodeType, weight = 1, width=None, height=None, intersectRadius=None):
    global counter
    global creationCalcs
    global updateCalcs

    newNode,newPosition = calculateNewPosition(G, node, theta, length)
    newRoadAndType = newRoadType + newNodeType;

    # Check if the new edge intersects with any existing edge
    closestIntersection = findClosestIntersection(G, node, newPosition)
    if closestIntersection:
        newPosition = closestIntersection

    tooCloseNode = checkProximity(G, newPosition, intersectRadius)

    G.nodes[node]['nodeType'] = changeNodeTo # change the node type of the current node

    newDirection = (newPosition[0] - G.nodes[node]['pos'][0], newPosition[1] - G.nodes[node]['pos'][1]) # calculate the direction of the new edge

    if tooCloseNode:
        if node != tooCloseNode:
            G.add_edge(node, tooCloseNode,weight=weight)
    else:
        G.add_node(newNode, nodeType=newNodeType, pos=newPosition, incEdge=newDirection, roadType = newRoadType) # add the new node to the graph
        G.add_edge(node, newNode,weight=weight)




productionRulesCityDict = {
    "mStart": [
        {
            "occurProb":     1,
            "changeNodeTo":  "T",
            "thetas":        [0, math.pi], 
            "lengths":       [1, 1], 
            "newRoadTypes":  ['m', 'm'], 
            "newNodeTypes":  ['L', 'L'], 
            "minDistances":  {}
        }
    ],
    "mL": [
        {   # Just a straight main road, with slight variation in the angle
            "occurProb":     0.1,
            "changeNodeTo":  "T",
            "thetas":        [[0,0.2]],
            "lengths":       [1], 
            "newRoadTypes":  ['m'],
            "newNodeTypes":  ['L'], 
            "minDistances":  {}
        },
        {   # A straight road with variation, and a new branch of main road
            "occurProb":     0.3,
            "changeNodeTo":  "B",
            "thetas":        [0,[math.pi/5,4*math.pi/5]],
            "lengths":       [1,2], 
            "newRoadTypes":  ['m','m'],
            "newNodeTypes":  ['L','L'], 
            "minDistances":  {"mB":3,"lB":3}
        },
        {   # A straight road with variation, and a new branch of large road
            "occurProb":     1,
            "changeNodeTo":  "B",
            "thetas":        [0,[math.pi/5,4*math.pi/5]],
            "lengths":       [1,2], 
            "newRoadTypes":  ['m','l'],
            "newNodeTypes":  ['L','L'], 
            "minDistances":  {"mB":3,"lB":3}
        }

    ],
    "lL": [
        {   # Just a straight large road, with slight variation in the angle
            "occurProb":     0.2,
            "changeNodeTo":  "T",
            "thetas":        [[0,0.2]],
            "lengths":       [1], 
            "newRoadTypes":  ['l'],
            "newNodeTypes":  ['L'], 
            "minDistances":  {}
        },
        {   # A straight road with variation, and a new branch of large road
            "occurProb":     0.8,
            "changeNodeTo":  "B",
            "thetas":        [0,[math.pi/5,4*math.pi/5]],
            "lengths":       [1,2], 
            "newRoadTypes":  ['l','l'],
            "newNodeTypes":  ['L','L'], 
            "minDistances":  {"mB":3,"lB":3}
        },
        {   # A straight road with variation, and a new branch of small road
            "occurProb":     0.8,
            "changeNodeTo":  "B",
            "thetas":        [0,[math.pi/3,2*math.pi/3]],
            "lengths":       [1,2], 
            "newRoadTypes":  ['l','s'],
            "newNodeTypes":  ['L','L'], 
            "minDistances":  {"mB":1,"lB":3}
        }

    ],
    "sL": [
        {
            "occurProb":     1,
            "changeNodeTo":  "B",
            "thetas":        [[1.5,1.6],[-1.6,-1.5]],
            "lengths":       [1,2],
            "newRoadTypes":  ['s','s'],
            "newNodeTypes":  ['L','L'],
            "minDistances":  {}
        }
    ],
}

production_rules = {
    'ruleCity': productionRulesCityDict
}




def generateCity(iterations, rule, width=None, height=None, intersectRadius=None, plotType="Map", showNodes = False, nodeLabelType = None, edgeLabelType = None, show=True):

    G.add_node(0, nodeType='Start', roadType="m", pos=(0,0), incEdge=(0,1)) # incEdge is the direction of the incoming edge
    
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
        elif nodeLabelType == "Road Type":
            with_labels = True
            labels=nx.get_node_attributes(G, 'roadType')
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

    def applyLSystem():
        global counter
        nodes = list(G.nodes())  # Create a copy of the nodes
        for node in nodes:

            nodeRoadAndType = G.nodes[node]['roadType'] + G.nodes[node]['nodeType']
            #choose one of the rules based on occurProb

            #if there is no rule for nodes of this type, skip this node
            if nodeRoadAndType not in production_rules['ruleCity']:
                continue
            rules = production_rules['ruleCity'][nodeRoadAndType]
            occurProbs = [rule['occurProb'] for rule in rules]
            #if the sum of the occurProbs is not 1, normalize them
            if sum(occurProbs) != 1:
                occurProbs = [prob/sum(occurProbs) for prob in occurProbs]
            #create a list of numbers from 0 to the length of the rules list
            ruleIndices = list(range(len(rules)))
            #randomly select one of the rules based on the occurProbs
            idealRuleIndex = np.random.choice(ruleIndices, p=occurProbs)
            #create a random permutation of ruleIndices, but ensure that the idealRuleIndex is in the first position
            ruleIndices.remove(idealRuleIndex)
            random.shuffle(ruleIndices)
            ruleIndices.insert(0,idealRuleIndex)

            """
            for ruleIndex in ruleIndices:
                rule = rules[ruleIndex]
                #check if the rule can be applied by checking the minDistances
                if not all([G.nodes[node]['minDistances'][nodeType] >= minDistance for nodeType,minDistance in rule['minDistances'].items()]):
                    continue #if the rule cannot be applied, skip it
                else:
                    break #if the rule can be applied, break out of the loop and apply it
            """

            #check if the rule can be applied, by calculating the minDistances to all nodes of the types in the rule
            for ruleIndex in ruleIndices:
                rule = rules[ruleIndex]
                minDistances = {}
                for nodeType in rule['minDistances']:
                    minDistances[nodeType] = calcMinDistanceToType(G, G.nodes[node]['pos'], nodeType)
                    counter += 1
                if not all([minDistances[nodeType] >= minDistance for nodeType,minDistance in rule['minDistances'].items()]):
                    continue
                else:
                    break


            if not len(rule['thetas']) == len(rule['lengths']) == len(rule['newRoadTypes']) == len(rule['newNodeTypes']):
                raise Exception("The number of thetas, lengths, newRoadTypes and newNodeTypes must be the same")
            for i in range(len(rule['thetas'])):
                if type(rule['thetas'][i]) == list:
                    theta = get_random_theta(rule['thetas'][i][0],rule['thetas'][i][1])
                else:
                    theta = rule['thetas'][i]
                
                if rule['newRoadTypes'][i]=="m":
                    weight = 1
                elif rule['newRoadTypes'][i]=="l":
                    weight = 0.5
                elif rule['newRoadTypes'][i]=="s":
                    weight = 0.25

                createNodes(G, node, rule['changeNodeTo'], theta, rule['lengths'][i], rule['newRoadTypes'][i], rule['newNodeTypes'][i], weight=weight, intersectRadius=intersectRadius)

    def update(i):
        print(f"Starting iteration: {i+1}/{iterations}")
        ax.clear()

        applyLSystem()

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
            applyLSystem()

        if plotType == "Map":
            graphSettings()
            """
            #set the axis limits
            ax.set_xlim([-5,5])
            ax.set_ylim([-5,5])
            """
            if show:
                plt.show()

    #return the graph object
    return G

#G = generateCity(100, 'ruleCity2', intersectRadius=1.5, showNodes=False, plotType="Map",nodeLabelType=None, width=120, height=120)
G = generateCity(50, 'ruleCity', intersectRadius=0.5, showNodes=False, plotType="Animation",nodeLabelType="None",show=True)

#print("Calculated a total of " + str(counter) + " minDistances")

