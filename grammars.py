import math

# Define a class to hold the grammars for the different types of road networks
# Each grammar holds a dictionary of rules for each roadType, nodeType combination, with the following structure:
# 
# "roadType+nodeType": [
    #       {
    #   "occurProb":     The probability that, given this roadType, nodeType combination, this rule will be applied (if these do not sum to 1 for each combination, the rules with be normalised)
    #   "changeNodeTo":  The nodeType that the current node will be changed to
    #   "thetas":        The angles of the new roads, relative to the current road. This is a list with a length that represents how many new roads will be created. Each element of the list is either a single value, or a list of two values. If it is a single value, the angle of the new road will be the same as the current road, plus or minus the value. If it is a list of two values, the angle of the new road will be a random value between the two values in the list.
    #   "lengths":       The lengths of the new roads. This is a list with a length that represents how many new roads will be created. Each element of the list is a single value, representing the length of each new road.
    #   "newRoadTypes":  The roadTypes of the new roads. This is a list with a length that represents how many new roads will be created. Each element of the list is a single value, representing the roadType of each new road.
    #   "newNodeTypes":  The nodeTypes of the new nodes. This is a list with a length that represents how many new roads will be created. Each element of the list is a single value, representing the nodeType of each new node.
    #   "minDistances":  A dictionary of minimum distances between the new node and existing nodes. The keys of the dictionary are the roadType, nodeType combination of the existing nodes, and the values are the minimum distances between the new node and the existing nodes of that combination. If the new node is too close to an existing node according to these restrictions, the rule will not be applied.
    #       }
    #   ],

class grammars:
    # The 'Organic' grammar creates a network that resembles a city with an organic layout, i.e. one that was built over time without much planning
    Organic = {
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

    # The 'Grid' grammar creates a network that resembles a city with a grid layout
    Grid = {
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
                "thetas":        [0],
                "lengths":       [1], 
                "newRoadTypes":  ['m'],
                "newNodeTypes":  ['L'], 
                "minDistances":  {}
            },
            {   # A straight road with variation, and a new branch of main road
                "occurProb":     0.3,
                "changeNodeTo":  "B",
                "thetas":        [0,math.pi/2],
                "lengths":       [1,1], 
                "newRoadTypes":  ['m','m'],
                "newNodeTypes":  ['L','L'], 
                "minDistances":  {"mB":3,"lB":3}
            },
            {   # A straight road with variation, and a new branch of large road
                "occurProb":     1,
                "changeNodeTo":  "B",
                "thetas":        [0,math.pi/2],
                "lengths":       [1,1], 
                "newRoadTypes":  ['m','l'],
                "newNodeTypes":  ['L','L'], 
                "minDistances":  {"mB":3,"lB":3}
            }

        ],
        "lL": [
            {   # Just a straight large road, with slight variation in the angle
                "occurProb":     0.2,
                "changeNodeTo":  "T",
                "thetas":        [0],
                "lengths":       [1], 
                "newRoadTypes":  ['l'],
                "newNodeTypes":  ['L'], 
                "minDistances":  {}
            },
            {   # A straight road with variation, and a new branch of large road
                "occurProb":     0.8,
                "changeNodeTo":  "B",
                "thetas":        [0,math.pi/2],
                "lengths":       [1,1], 
                "newRoadTypes":  ['l','l'],
                "newNodeTypes":  ['L','L'], 
                "minDistances":  {"mB":3,"lB":3}
            },
            {   # A straight road with variation, and a new branch of small road
                "occurProb":     0.8,
                "changeNodeTo":  "B",
                "thetas":        [0,math.pi/2],
                "lengths":       [1,1], 
                "newRoadTypes":  ['l','s'],
                "newNodeTypes":  ['L','L'], 
                "minDistances":  {"mB":1,"lB":3}
            }

        ],
        "sL": [
            {
                "occurProb":     1,
                "changeNodeTo":  "B",
                "thetas":        [0,math.pi/2],
                "lengths":       [1,1],
                "newRoadTypes":  ['s','s'],
                "newNodeTypes":  ['L','L'],
                "minDistances":  {}
            }
        ],
    }

