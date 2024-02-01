from grammars import grammars
from lSystems import CityGenerator

# Create an instance of the CityGenerator class
cityGen = CityGenerator()

# Call the generateCity method on the instance
G = cityGen.generateCity(20, grammars.Organic, seed=1, intersectRadius=0.5, showNodes=False, plotType="Map",nodeLabelType="None", show=True)
