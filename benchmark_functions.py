import math

def rosenbrock(x, y):
    return (-x)**2 + 100*(y - x**2)**2


def rastrigin(x, y):
    return 20 + (x**2 - 10 * math.cos(2 * math.pi * x)) + (y**2 - 10 * math.cos(2 * math.pi * y))