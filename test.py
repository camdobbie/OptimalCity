from cityGenerator import CityGenerator
from grammars import grammars

cityGen = CityGenerator()

G = cityGen.generateCity(40, grammars.Organic, seed=1, intersectRadius=0.5,  plotType="Map")