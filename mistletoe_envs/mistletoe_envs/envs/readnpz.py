import numpy as np
from matplotlib import pyplot as plt

b = np.load('./eval_logs/evaluations.npz')

plt.title("Matplotlib demo") 
plt.xlabel("x axis caption") 
plt.ylabel("y axis caption") 
plt.plot(b['timesteps'],b['results']) 
plt.show()