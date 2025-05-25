import pygame
from os.path import join

GREEN = (0, 200, 0)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        # self.image = pygame.Surface((width, height))
        # self.image.fill(GREEN)
        self.image = pygame.image.load(join('images', 'p1.png'))
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))