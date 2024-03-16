from grammars import grammars
from cityGenerator import CityGenerator
import optimisationMetrics as optim
import generateMaps as maps
import pickle
import matplotlib.pyplot as plt

# The organic grammar is the most similar to real cities, so we will use this to calculate the correct person per square kilometre

# As of mid 2021, London had a population of 8.797 million
# https://data.london.gov.uk/dataset/londons-population

#London has an area of 1,572 square km
#https://www.britannica.com/place/Greater-London

#Therefore, London has a population density of 5,596 people per square kilometre.
# This is the population density we will aim for in organic cities 

# run for 50 iterations the organic one, assign correct person per m road 

mode = "banana" # "generate" or "plot"

cityGen = CityGenerator()

if mode == "generate":

    maxIterations =     100000000
    #grammar =           "Line" #For line, use a maxWidth of 16
    #seed =              0
    #population =        100000
    maxHeight =         None # 10km

    """
    grammarList = ["Grid","Hex","Line","Organic"]
    seedList = [0,1,2,3,4]
    populationList = [100000, 500000, 1000000, 5000000]
    """

    grammarList = ["Organic", "Line", "Hex", "Grid"]
    seedList = [0,1,2,3,4]
    populationList = [5000000]

    for population in populationList:
        for grammar in grammarList:
            grammarDict = getattr(grammars, grammar)
            if grammar == "Line":
                maxWidth = 16
            else:
                maxWidth = None

            for seed in seedList:
                fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"

                if population == 5000000:
                    complexityPath = None#f"statsAndFigs/{grammar}/{grammar}Population{population}seed{seed}Complexity.txt"
                else:
                    complexityPath = None

                print(f"Generating city with grammar: {grammar} and seed: {seed} and population: {population}")
                G = cityGen.generateCity(maxIterations, grammarDict, seed=seed, intersectRadius=0.8,  plotType=None, maxWidth=maxWidth, maxHeight=maxHeight, population=population, complexityPath=complexityPath)
                cityGen.saveCity(G, fileName)
                cityGen.clearGraph()

    #print(f"Population:          {optim.calculatePopulation(G)}")
    #print(f"Population density:  {optim.calculatePopulationDensity(G, maxWidth, maxHeight)} people per square kilometre")


elif mode == "saveBlackCities":
    seed = 0
    population = 500000
    grammarList = ["Line"]

    for grammar in grammarList:

        fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"
        G = cityGen.loadCity(fileName)
        #save the figure
        figName = f"statsAndFigs/figs/cityPlots/{grammar}Population{population}seed{seed}Black.pdf"
        optim.plotCityBlack(G,show=False,savePath=figName)


elif mode == "pickleBetweenness":
    seedList = [0,1,2,3,4]
    grammarList = ["Organic", "Hex", "Grid", "Line"]
    population = 100000

    for grammar in grammarList:
        for seed in seedList:
            fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"
            G = cityGen.loadCity(fileName)
            savePath = f"statsAndFigs/betweennessData/{grammar}Population{population}seed{seed}Betweenness.txt"
            betweenness = optim.calculateRoadBetweennessCentrality(G,savePath=savePath)

elif mode == "plotBetweenness":
    grammar = "Organic"
    population = 100000
    seed = 0

    fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"
    G = cityGen.loadCity(fileName)
    maps.plotRoadsByClusteredBetweennessCentrality(G,betweennessLoadPath=f"statsAndFigs/betweennessData/{grammar}Population{population}seed{seed}Betweenness.txt")


population = 1000000
seed = 0
grammar = "Organic"
fileName = f"savedCities/{grammar}/{population}/{grammar}Population{population}seed{seed}.pkl"
G = cityGen.loadCity(fileName)
alphas = [0.01, 0.05, 0.5]
for alpha in alphas:
    maps.plotCityBlackWithAlphaShape(G, alpha = alpha, savePath=f"C:/Users/camer/Uni Documents/Year 4/Technical Project/Report/Figures/Alpha{alpha}.pdf", show=False)