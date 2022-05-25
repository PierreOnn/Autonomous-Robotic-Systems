# Author: Pierre Onghena

import pygame
import random


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super(Wall, self).__init__()
        self.id = random.randint(0, 9)
        self.surf = pygame.Surface((width, height))
        self.surf.fill((255, 0, 0))
        self.rect = self.surf.get_rect(center=(x, y))
