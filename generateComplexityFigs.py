import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('statsAndFigs/organicSeed9Complexity.txt', sep=',', header=None)
# Assign column names
df.columns = ['Nodes before iteration', 'Time taken to complete iteration (s)']

#fit a polynomial to the data
z = np.polyfit(df['Nodes before iteration'], df['Time taken to complete iteration (s)'], 2)
p = np.poly1d(z)

#print the coefficients
print(p)

#plot the data
plt.scatter(df['Nodes before iteration'], df['Time taken to complete iteration (s)'])
plt.plot(df['Nodes before iteration'], p(df['Nodes before iteration']), 'r--')
plt.xlabel('Nodes before iteration')
plt.ylabel('Time taken to complete iteration (s)')
plt.title('Organic Seed 9 Complexity')
#add a legend
plt.legend(['Polynomial of Degree 2', 'Data'])
plt.show()
