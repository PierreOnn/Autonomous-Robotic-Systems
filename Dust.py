# Author: Pierre Onghena

import pygame
import random


# Class to simulate the dust particles is our simulation.
class Dust(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Dust, self).__init__()
        self.id = random.randint(9, 1000)
        self.surf = pygame.Surface((2, 2))
        self.surf.fill((192, 192, 192))
        self.rect = self.surf.get_rect(center=(x, y))