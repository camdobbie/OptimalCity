from grammars import grammars
from cityGenerator import CityGenerator
import optimisationMetrics as optim
import pickle

# Bristol has approximately 3,892 people per km^2
# London has approximately 5,671 people per km^2
# I will therefore use a population density of 5000 people per km^2 as a rough estimate for a city.

# A test city has a calculated population of 5000 * 100 = 500,000 people
# This city has a total road length of 7388hm
# The city therefore has a person per hm of road value of 67.68 people per hm of road


mode = "generate"

cityGen = CityGenerator()

maxIterations =     10000
grammar =           "Line" #For line, use a maxWidth of 16
#seed =              0
population =        100000
maxHeight =         None # 10km
maxWidth =          16 # 10km

grammarList = ["Organic", "Hex", "Grid", "Line"]
seedList = [1,2,3,4]
populationList = [100000, 1000000, 5000000]

grammarDict = getattr(grammars, grammar)

"""
if maxHeight and maxWidth:
    fileName = f"savedCities/{grammar}{maxWidth}x{maxHeight}seed{seed}.pkl"
"""

"""
fileName = f"savedCities/{grammar}Population{population}seed{seed}.pkl"
"""

if mode == "generate":
    for grammar in grammarList:
        for seed in seedList:
            fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"
            print(f"Generating city with grammar: {grammar} and seed: {seed} and population: {population}")
            G = cityGen.generateCity(maxIterations, grammarDict, seed=seed, intersectRadius=0.5,  plotType=None, maxWidth=maxWidth, maxHeight=maxHeight, population=population)
            cityGen.saveCity(G, fileName)
            cityGen.clearGraph()

    #print(f"Population:          {optim.calculatePopulation(G)}")
    #print(f"Population density:  {optim.calculatePopulationDensity(G, maxWidth, maxHeight)} people per square kilometre")

"""
elif mode == "plot":
    G = cityGen.loadCity(fileName)
    optim.plotCityBlackWithHull(G)
    optim.calculatePopulationDensity(G)
"""
