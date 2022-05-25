# Authors: Rick van Bellen, Tim Debets

import collections
import random
from NeuralNetwork import RNN
from copy import deepcopy
from plot import *
from simulation import *
from utility import euclidean_distance


# Check if both the lists are of same length and then get the frequency
# of each element in list using collections.Counter. Then Compare if both the Counter
# objects are equal or not to confirm if lists contain similar elements with same frequency
def check_if_equal_2(list_1, list_2):
    if len(list_1) != len(list_2):
        return False
    return collections.Counter(list_1) == collections.Counter(list_2)


class EvolutionaryAlgorithm:
    # Creates population_size different initial robots with random weights and returns them as a list
    def initialize(self, population_size):
        population = []
        for i in range(population_size):
            genome = np.random.uniform(-1, 1, 72)
            population.append(genome)
        return population

    # Evaluate the individuals in the population
    def evaluate(self):
        evaluations = []
        test_evaluations = []
        for individual in self.population:
            # Re-adjust the genome in such away we can immediately use it in the network
            wxh = np.array(individual[0:48]).reshape(12, 4)
            why = np.array(individual[48:56]).reshape(4, 2)
            whh = np.array(individual[56:]).reshape(4, 4)
            network = RNN(wxh, why, whh)
            value = network_play(network, False, settings.TRAINING_TIME_STEPS, "train", 0)
            test_value = network_play(network, False, settings.TRAINING_TIME_STEPS, "test", 0)
            evaluations.append(value)
            test_evaluations.append(test_value)
        self.evaluations = evaluations
        self.test_evaluations = test_evaluations

    # Uses truncated rank-based selection with generational replacement
    def select_and_reproduce(self, x):
        N = len(self.population)
        # Get the x highest evaluation indices
        ind = np.argpartition(np.array(self.evaluations), -x)[-x:]
        best_robots = np.array(self.population)[ind]
        best_robots = best_robots.tolist()
        self.population = []
        for robot in best_robots:
            for i in range(int(N / x)):
                self.population.append(deepcopy(robot))

    # singlepoint crossover
    # prob_cross is always 1, so we always do a crossover
    def crossover_mutation(self, prob_cross, prob_mut):
        rand_prob = random.random()
        if rand_prob < prob_cross:
            parent1 = random.randint(0, len(self.population) - 1)
            parent2 = random.randint(0, len(self.population) - 1)
            parent1_copy = deepcopy(self.population[parent1])
            parent2_copy = deepcopy(self.population[parent2])

            # don't want the cross over to start from very first chromosome, otherwise you don't get a crossover
            cross_point = random.randint(1, len(parent1_copy) - 1)
            child1 = []
            child2 = []
            for chromosome in range(0, cross_point):
                child1.append(parent1_copy[chromosome])
                child2.append(parent2_copy[chromosome])
            for chromosome in range(cross_point, len(parent1_copy)):
                child1.append(parent2_copy[chromosome])
                child2.append(parent1_copy[chromosome])
            self.population[parent1] = child1
            self.population[parent2] = child2

        # Mutation, every chromosome of a genome for every individual has
        # prob_mut chance of mutating
        for index, individual in enumerate(self.population):
            for indexc, chromosome in enumerate(individual):
                rand_prob = random.random()
                if rand_prob < prob_mut:
                    new_chromosome = random.uniform(-1, 1)
                    individual[indexc] = new_chromosome

        # After cross over and mutation, check whether population is unique
        unique = False
        while not unique:
            unique = True
            for i in range(len(self.population)):
                for j in range(i + 1, len(self.population)):
                    result = check_if_equal_2(self.population[i], self.population[j])
                    if result:
                        unique = False
                        for indexc, chromosome in enumerate(self.population[i]):
                            rand_prob = random.random()
                            if rand_prob < prob_mut:
                                new_chromosome = random.uniform(0, 1)
                                self.population[j][indexc] = new_chromosome
                        for indexc, chromosome in enumerate(self.population[j]):
                            rand_prob = random.random()
                            if rand_prob < prob_mut:
                                new_chromosome = random.uniform(0, 1)
                                self.population[j][indexc] = new_chromosome

    # Average + best solution of the fitness
    def evaluating_evaluations(self):
        return np.average(self.evaluations), np.amax(self.evaluations), \
               np.average(self.test_evaluations), np.amax(self.test_evaluations)

    # Do a network play while showing the result
    def show_best_individual(self, generation):
        individual = self.population[0]
        wxh = np.array(individual[0:48]).reshape(12, 4)
        why = np.array(individual[48:56]).reshape(4, 2)
        whh = np.array(individual[56:]).reshape(4, 4)
        network = RNN(wxh, why, whh)
        network_play(network, True, 1000, "train", generation)
        network_play(network, True, 1000, "test", generation)

    def __init__(self):
        self.average_fitness = []
        self.best_fitness = []
        self.average_test_fitness = []
        self.best_test_fitness = []
        self.population = []
        self.evaluations = []
        self.test_evaluations = []
        self.diversity = []


# This main method is also solely for testing purposes
if __name__ == "__main__":
    ea = EvolutionaryAlgorithm()
    ea.population = ea.initialize(settings.POPULATION)
    # For a number of generations
    for i in range(settings.NUM_GENERATIONS):
        print(f"Generation {i}")
        # Evaluate all of the population
        ea.evaluate()
        # Get the statistics
        statistics = ea.evaluating_evaluations()
        ea.average_fitness.append(statistics[0])
        ea.best_fitness.append(statistics[1])
        ea.average_test_fitness.append(statistics[2])
        ea.best_test_fitness.append(statistics[3])
        # Get the diversity of the population, calculated with euclidean_distance
        ea.diversity.append(euclidean_distance(ea.population))
        # Select, reproduce, crossover and mutation
        ea.select_and_reproduce(settings.SELECTION_RANK)
        ea.crossover_mutation(settings.CROSSOVER_PROBABILITY, settings.MUTATION_PROBABILITY)
        # Reset the evaluations
        ea.evaluations = []
        ea.test_evaluations = []
        if (i + 1) % 10 == 0:
            ea.show_best_individual(i + 1)
    plt.plot(ea.average_fitness, label='Average Training Fitness')
    plt.plot(ea.best_fitness, label='Best Training Fitness')
    plt.plot(ea.average_test_fitness, label='Average Test Fitness')
    plt.plot(ea.best_test_fitness, label='Best Test Fitness')
    plt.title('fitness')
    plt.legend(loc="upper right")
    plt.savefig('fitness.png')
    plt.show()
    plt.plot(ea.diversity)
    plt.title('Diversity')
    plt.savefig('Diversity.png')
    plt.show()
