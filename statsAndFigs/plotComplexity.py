#complexity.txt is a file with x values in the first column and y values in the second column, separated by a space. read in the file and plot the data.

import matplotlib.pyplot as plt
import numpy as np

#read in the file
data = np.loadtxt("complexity.txt")

#plot the data
plt.plot(data[:,0], data[:,1], 'ro')
plt.xlabel("Iterations")
plt.ylabel("Time (s)")
plt.title("Complexity of City Generation")

plt.show()
