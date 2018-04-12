__author__ = 'william'

import numpy as np

import matplotlib.pyplot as plt
plt.clf()
t = np.loadtxt('dome_bench.txt', usecols=(0, 1, 2)).T
delta_angle = t[0] - t[1]
plt.plot(-delta_angle[delta_angle < 0], t[2][delta_angle < 0], '.', color='blue', label='back')
plt.plot(delta_angle[delta_angle > 0], t[2][delta_angle > 0], '.', color='green', label='forward')
mean = [np.mean(t[2][np.abs(delta_angle) == x]) for x in np.unique(np.abs(delta_angle))]
plt.plot(np.unique(np.abs(delta_angle)), mean, color='black', label='mean')
plt.xlim(10, 370)
plt.legend(loc=2)
plt.xlabel('Angle (deg)')
plt.ylabel('Slew time (sec)')
plt.savefig('dome_bench.png')
