# Author: Rick van Bellen

import numpy as np
import math


# Sigmoid activation function
def sigmoid(input):
    new_input = np.zeros(input.shape)
    for i in range(len(input)):
        new_input[i] = 1 / (1 + math.exp(-1 * input[i]))
    return new_input


# tanh activation function
def tanh(input):
    return np.tanh(input)


# class that defines the neural network
class RNN():
    def __init__(self, Wxh, Why, Whh):
        self.Wxh = Wxh
        self.Why = Why
        self.Whh = Whh
        self.h_previous = np.zeros(Whh.shape[0])

    # Define the robot movement
    def feed_forward(self, x):
        h_x = np.dot(x, self.Wxh)
        h_from_previous = np.dot(self.h_previous, self.Whh)
        h = tanh(h_x + h_from_previous)
        self.h_previous = h
        y = np.dot(h, self.Why)
        return y


# This is just code to test the neural network, so not needed for the actual program
if __name__ == "__main__":
    Wxh = np.random.uniform(-1, 1, (12, 4))
    Why = np.random.uniform(-1, 1, (4, 2))
    Whh = np.random.uniform(-1, 1, (4, 4))
    rnn = RNN(Wxh, Why, Whh)
    x = np.random.rand(12)
    print(rnn.feed_forward(x))
    x2 = np.random.rand(12)
    print(rnn.feed_forward(x2))
