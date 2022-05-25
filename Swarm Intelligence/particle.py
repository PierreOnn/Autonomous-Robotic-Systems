import numpy as np

class Particle:
    def __init__(self, s, v, benchmark):
        # Location of the particle
        self.s = s
        # Angle and distance of the particle
        self.v = v
        # Performance (value of function at current location)
        self.f = 0
        self.set_performance(benchmark)
        # List of neighbors
        self.neighbors = []
        self.gbest = None
        self.s_pbest = s
        self.f_pbest = self.f


    def move(self, benchmark, x_min, x_max, y_min, y_max):
        # Move the particle, and clip to the borders
        self.s += self.v
        if self.s[0] < x_min:
            self.s[0] = x_min
        if self.s[0] > x_max:
            self.s[0] = x_max
        if self.s[1] < y_min:
            self.s[1] = y_min
        if self.s[1] > y_max:
            self.s[1] = y_max
        self.set_performance(benchmark)
        self.update_pbest()

    def set_velocity(self, v):
        self.v = v

    def set_performance(self, benchmark):
        self.f = benchmark(self.s[0], self.s[1])

    def update_gbest(self):
        f_min = 100000000
        for g in self.neighbors:
            if g.f < f_min:
                f_min = g.f
                gbest = g
        self.gbest = gbest

    def update_pbest(self):
        if self.f < self.f_pbest:
            self.f_pbest = self.f
            self.s_pbest = self.s

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)

    def update_local_neighbors(self, particles_list):
        particles_list_copy = particles_list.copy()
        particles_list_copy.sort(key=lambda p: np.linalg.norm(p.s - self.s))
        self.neighbors = particles_list_copy[1:5]