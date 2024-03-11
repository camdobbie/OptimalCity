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


mode = "plot" # "generate" or "plot"

cityGen = CityGenerator()

"""
if maxHeight and maxWidth:
    fileName = f"savedCities/{grammar}{maxWidth}x{maxHeight}seed{seed}.pkl"
"""

"""
fileName = f"savedCities/{grammar}Population{population}seed{seed}.pkl"
"""

if mode == "generate":

    maxIterations =     100000000
    #grammar =           "Line" #For line, use a maxWidth of 16
    #seed =              0
    #population =        100000
    maxHeight =         None # 10km

    grammarList = ["Grid","Hex","Line","Organic"]
    seedList = [0,1,2,3,4]
    populationList = [5000000]

    #grammarDict = getattr(grammars, grammar)
    for population in populationList:
        for grammar in grammarList:
            grammarDict = getattr(grammars, grammar)
            if grammar == "Line":
                maxWidth = 16
            else:
                maxWidth = None

            for seed in seedList:
                fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"
                complexityPath = f"statsAndFigs/{grammar}Population{population}seed{seed}Complexity.txt"
                print(f"Generating city with grammar: {grammar} and seed: {seed} and population: {population}")
                G = cityGen.generateCity(maxIterations, grammarDict, seed=seed, intersectRadius=0.5,  plotType=None, maxWidth=maxWidth, maxHeight=maxHeight, population=population, complexityPath=complexityPath)
                cityGen.saveCity(G, fileName)
                cityGen.clearGraph()

    #print(f"Population:          {optim.calculatePopulation(G)}")
    #print(f"Population density:  {optim.calculatePopulationDensity(G, maxWidth, maxHeight)} people per square kilometre")


elif mode == "plot":
    seed = 0
    population = 5000000
    grammar = "Grid"

    fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"
    G = cityGen.loadCity(fileName)
    #optim.calculateAlphaShapePopulationDensity(G)
    #optim.calculateConvexHullPopulationDensity(G)
    #optim.plotCityBlackWithAlphaShape(G)

#cityGen.generateCity(1000000, grammars.Line, seed=0, intersectRadius=0.5,  plotType="Map", maxWidth=16, maxHeight=None,population=1000000)