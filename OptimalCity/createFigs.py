from lSystemsV3 import generateCity
import matplotlib.pyplot as plt

G = generateCity(25, 'ruleCity', intersectRadius=0.5, showNodes=False, plotType="Map",show=False)
plt.axis('off')
plt.grid(False)

#set the limits of the axis to the limits of the city
plt.xlim([min([G.nodes[node]['pos'][0] for node in G.nodes]),max([G.nodes[node]['pos'][0] for node in G.nodes])])
plt.ylim([min([G.nodes[node]['pos'][1] for node in G.nodes]),max([G.nodes[node]['pos'][1] for node in G.nodes])])

# Adjust subplot parameters to remove empty border
plt.tight_layout()

plt.savefig('seed2iter25.png', dpi=300, bbox_inches='tight')
