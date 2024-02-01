from lSystems import generateCity
import time
import matplotlib.pyplot as plt

iterations = 70

startTime = time.time()
generateCity(iterations, 'ruleCity', intersectRadius=0.5, showNodes=False, plotType="Map",nodeLabelType="None", show=False)
endTimes = time.time()

#write the time to "iterations" line of the file "complexity.txt"
with open("complexity.txt", "a") as myfile:
    myfile.write(str(iterations) + " " + str(endTimes - startTime) + "\n")

