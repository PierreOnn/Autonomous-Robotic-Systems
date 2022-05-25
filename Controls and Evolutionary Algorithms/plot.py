# Author: Tim Debets

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from benchmark_functions import rosenbrock, rastrigin


# Plotting the function with global minimum as a point
def plot(function, x_min, x_max, y_min, y_max, step):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    X = np.arange(x_min, x_max, step)
    Y = np.arange(y_min, y_max, step)
    X, Y = np.meshgrid(X, Y)
    # Due to implementation of the benchmark functions, to create the surface, different steps are needed
    if function == rastrigin:
        function = np.vectorize(rastrigin)
        Z = function(X,Y)
        ax.plot_surface(X, Y, Z, cmap='Blues',
                       linewidth=0, alpha=0.2, rstride=1, cstride=1)
    if function == rosenbrock:
        Z = function(X,Y)
        ax.plot_surface(X, Y, Z, cmap=cm.gist_heat_r,
                               linewidth=0, alpha=0.8, rstride=1, cstride=1)
    ax.plot([0], [0], [function(0, 0)], marker='*', markersize=10, color='k', alpha=1)

    return ax


# Plotting a particle on the grid
def plot_points(ax, particle, benchmark):
    ax.plot([particle[0]], [particle[1]], [benchmark(particle[0], particle[1])], marker='x', markersize=1, color='b', alpha=1)

