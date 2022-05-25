from benchmark_functions import rosenbrock, rastrigin
from particle import Particle
import random
import numpy as np
from matplotlib import cm
from plot import plot
import matplotlib.pyplot as plt


def pso(benchmark, x_min, x_max, y_min, y_max, v_max, num_iterations, neighborhood, step):
    # Initialize the particles
    particles_list = []
    for i in range(5):
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)
        s = np.array([x, y])
        v = np.random.rand(2)
        if np.linalg.norm(v) > v_max:
            v = v/np.linalg.norm(v) * v_max
        particle = Particle(s, v, benchmark)
        particles_list.append(particle)

    # Initialize the particles neighbors
    # Question by Tim: Aren't we just taking the next 3, in the lecture they take for example, the left and right neighbor,
    # not only the three right ones
    if neighborhood == "social":
        for i in range(len(particles_list)):
            n1 = i + 1
            n2 = i + 2
            n3 = i + 3
            if n1 >= len(particles_list):
                n1 = 0
                n2 = 1
                n3 = 2
            elif n2 >= len(particles_list):
                n2 = 0
                n3 = 1
            elif n3 >= len(particles_list):
                n3 = 0
            neighbors = [particles_list[n1], particles_list[n2], particles_list[n3]]
            particles_list[i].neighbors = neighbors
            particles_list[i].update_gbest()

    if neighborhood == "global":
        for i in range(len(particles_list)):
            for j in range(len(particles_list)):
                if i != j:
                    particles_list[i].add_neighbor(particles_list[j])
            particles_list[i].update_gbest()

    # Set up for image
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    X = np.arange(x_min, x_max, step)
    Y = np.arange(y_min, y_max, step)
    X, Y = np.meshgrid(X, Y)
    if benchmark == rastrigin:
        benchmark = np.vectorize(rastrigin)
        Z = benchmark(X,Y)
        surf = ax.plot_surface(X, Y, Z, cmap='Blues',
                       linewidth=0, alpha=0.2, rstride=1, cstride=1)
    else:
        Z = benchmark(X,Y)
        surf = ax.plot_surface(X, Y, Z, cmap=cm.gist_heat_r,
                               linewidth=0, alpha=0.8, rstride=1, cstride=1)


    # Do PSO
    for iteration in range(num_iterations):
        a = 0.9
        b = 2
        c = 2

        for p in particles_list:
            # Show particle on grid
            ax.plot([p.s[0]], [p.s[1]], [benchmark(p.s[0], p.s[1])], marker='x', markersize=10, color='k', alpha=1)

            # Update the local neighbors if necessary
            if neighborhood == "local":
                p.update_local_neighbors(particles_list)
            # Calculate the best neighbor
            p.update_gbest()
            # Calculate the new velocity
            R1 = random.random()
            R2 = random.random()
            new_velocity = a * p.v + b * R1 * (p.s_pbest - p.s) + c * R2 * (p.gbest.s - p.s)
            # Clip it to distance v_max
            if np.linalg.norm(new_velocity) > v_max:
                new_velocity = new_velocity / np.linalg.norm(new_velocity) * v_max
            # Move the particle and do the necessary updates
            p.set_velocity(new_velocity)
            p.move(benchmark, x_min, x_max, y_min, y_max)
        plt.pause(0.5)
        # Gradually reduce a
        a -= 0.5/num_iterations
    plt.show()

if __name__ == "__main__":
    benchmark = rosenbrock
    x_min = -2
    x_max = 2
    y_min = -2
    y_max = 3
    v_max = 0.25
    num_iterations = 5
    neighborhood = "global"
    pso(benchmark, x_min, x_max, y_min, y_max, v_max, num_iterations, neighborhood, 0.15)
    # plot("rosenbrock", -2, 2, -1, 3, 0.15)