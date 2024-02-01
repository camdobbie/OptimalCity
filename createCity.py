from lSystems import generateCity
from grammars import grammars

generateCity(25, grammars.Organic, seed=2, intersectRadius=0.5, showNodes=False, plotType="Map",nodeLabelType="None", show=True, benchmark=True)

#generateCity(40, 'ruleGrid', intersectRadius=0.5, showNodes=False, plotType="Map",nodeLabelType="None", show=True, benchmark=True)