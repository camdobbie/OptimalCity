import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection

# Define an object that will be used by the legend
class MulticolorPatch(object):
    def __init__(self, colors):
        self.colors = colors
        
# Define a handler for the MulticolorPatch object
class MulticolorPatchHandler(object):
    def legend_artist(self, legend, orig_handle, fontsize, handlebox):
        width, height = handlebox.width, handlebox.height
        patches = []
        for i, c in enumerate(orig_handle.colors):
            patches.append(plt.Rectangle([width/len(orig_handle.colors) * i - handlebox.xdescent, 
                                          -handlebox.ydescent],
                           width / len(orig_handle.colors),
                           height, 
                           facecolor=c, 
                           edgecolor='none'))

        patch = PatchCollection(patches, match_original=True)

        handlebox.add_artist(patch)
        return patch

class ComplexityPlotter:
    def __init__(self):
        self.grammarList = ["Organic", "Grid", "Hex", "Line"]
        self.seedList = [0,1,2,3,4]
        self.populationList = [5000000]
        self.colourPalettes = {
            "Grid": sns.color_palette("PuRd", len(self.seedList)),
            "Hex": sns.color_palette("Wistia", len(self.seedList)),
            "Line": sns.color_palette("Blues_d", len(self.seedList)),
            "Organic": sns.color_palette("Greens_d", len(self.seedList))
        }

    def quadFuncThroughOrigin(self, x, a, b):
        return a * x**2 + b * x

    def createDataFrame(self, grammar, population, seed):
        path = f"statsAndFigs/complexityData/{grammar}/{grammar}Population{population}seed{seed}Complexity.txt"
        df = pd.read_csv(path, sep=',', header=None)
        df.columns = ['Network size (nodes)', 'Time taken to reach size (seconds)']
        return df

    def createListOfExperimentalData(self):
        dfList = []
        dfKeys = []
        for population in self.populationList:
            for grammar in self.grammarList:
                for seed in self.seedList:
                    path = f"statsAndFigs/complexityData/{grammar}/{grammar}Population{population}seed{seed}Complexity.txt"
                    df = pd.read_csv(path, sep=',', header=None)
                    df.columns = ['Network size (nodes)', 'Time taken to reach size (seconds)']
                    dfList.append(df)
                    dfKeys.append((f"{grammar}", f"{seed}"))
        return dfList, dfKeys

    def addQuadraticFitThroughOrigin(self, df):
        popt, pcov = curve_fit(self.quadFuncThroughOrigin, df['Network size (nodes)'], df['Time taken to reach size (seconds)'])
        df['Quadratic fit'] = self.quadFuncThroughOrigin(df['Network size (nodes)'], *popt)
        return df

    def createListOfExperimentalAndFittedData(self):

        dfList, dfKeys = self.createListOfExperimentalData()
        for i, df in enumerate(dfList):
            dfList[i] = self.addQuadraticFitThroughOrigin(df)
        return dfList, dfKeys

    def plotAllCombinations(self,show=True):
        dfList, dfKeys = self.createListOfExperimentalAndFittedData()

        plt.rcParams['text.usetex'] = True
        sns.set_theme(style='darkgrid')

        fig, ax = plt.subplots()
        ax.set_xlabel('Network size (nodes)')
        ax.set_ylabel('Time taken to reach size (seconds)')

        handles = []
        labels = []

        for grammar in self.grammarList:
            # Create a MulticolorPatch for each grammar
            colors = self.colourPalettes[grammar]
            handles.append(MulticolorPatch(colors))
            labels.append(grammar)

        for i, df in enumerate(dfList):
            grammar, seed = dfKeys[i]
            color = self.colourPalettes[grammar][int(seed)]
            ax.plot(df['Network size (nodes)'], df['Quadratic fit'], label=dfKeys[i], color=color)

        # Use a custom handler to display multicolor legend patches
        ax.legend(handles, labels, loc='upper left', 
                 handler_map={MulticolorPatch: MulticolorPatchHandler()}, 
                 bbox_to_anchor=(.125,.875))
        
        plt.tight_layout()

        if show:
            plt.show()


    def plotSingleCombination(self, grammar, population, seed, show=True):
        df = self.createDataFrame(grammar, population, seed)
        
        df = self.addQuadraticFitThroughOrigin(df)

        plt.rcParams['text.usetex'] = True
        sns.set_theme(style='darkgrid')

        fig, ax = plt.subplots(figsize=(4, 8/3))
        ax.set_xlabel('Network size (nodes)')
        ax.set_ylabel('Time taken to \n reach size (seconds)')

        ax.scatter(df['Network size (nodes)'], df['Time taken to reach size (seconds)'], label="Experimental data", marker="x", color = 'black')
        ax.plot(df['Network size (nodes)'], df['Quadratic fit'], label="Quadratic fit", color=self.colourPalettes[grammar][3], linewidth=2)
#self.colourPalettes[grammar][0])

        plt.legend()
        plt.tight_layout()
        if show:
            plt.show()

    def saveSubplots(self, population, seed):
        for grammar in self.grammarList:
            self.plotSingleCombination(grammar, population, seed, show=False)
            plt.savefig(f"statsAndFigs/figs/complexityFigs/{grammar}Population{population}seed{seed}Complexity.pdf")

    def saveAllCombninations(self):
        self.plotAllCombinations(show=False)
        plt.savefig(f"statsAndFigs/figs/complexityFigs/AllCombinationsComplexity.pdf")

# Usage
plotter = ComplexityPlotter()

plotter.plotAllCombinations()

#plotter.saveAllCombninations()
#plotter.saveSubplots(5000000, 0)