from grammars import grammars
from cityGenerator import CityGenerator

# Create an instance of the CityGenerator class
cityGen = CityGenerator()

# Call the generateCity method on the instance
#G = cityGen.generateCity(120, grammars.Organic, seed=9, intersectRadius=0.5, showNodes=False, plotType="Map",nodeLabelType="None", show=False, complexityPath="statsAndFigs/organicSeed9Complexity.txt")
G = cityGen.generateCity(100, grammars.Organic, seed=9, intersectRadius=0.5, showNodes=False, plotType="Animation",nodeLabelType="None")
