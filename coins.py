import pygame
from os.path import join
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        # pygame.draw.circle(self.image, (255, 215, 0), (10, 10), 10)
        # self.rect = self.image.get_rect(center=(x, y))
        self.image = pygame.image.load(join('images', 'coin.gif'))
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect(center=(x, y))