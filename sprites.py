import pygame
from os.path import join
WIDTH, HEIGHT = 800, 600

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, frames):
        super().__init__()
        self.frames, self.frame_index, self.animation_speed = frames, 0, 10
        self.image = self.frames[self.frame_index]
        self.scale = 1/7
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.scale, self.image.get_height() * self.scale))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.on_ground = False
        self.speed = 5
        self.clock = pygame.time.Clock()
        self.dx = 0
        self.dy = 0
        self.facing_left = False

    def animate(self):
        if self.dx != 0:
            dt = self.clock.tick(60) / 1000
            self.frame_index += self.animation_speed * dt
            self.image = self.frames[int(self.frame_index) % len(self.frames)]
        else:
            self.frame_index = 0
            self.image = self.frames[0]

        if self.facing_left:
            self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.scale, self.image.get_height() * self.scale))

    def update(self, keys):
        self.dx = 0
        self.dy = 0
        if keys[pygame.K_a]:
            self.dx = -self.speed
            self.facing_left = True
        if keys[pygame.K_d]:
            self.dx = self.speed
            self.facing_left = False

        if keys[pygame.K_w] and self.on_ground:
            self.vel_y = -15
            self.on_ground = False

        self.vel_y += 0.8
        if self.vel_y > 10:
            self.vel_y = 10
        self.dy += self.vel_y

        self.rect.x += self.dx
        self.rect.y += self.dy

        self.animate()

        if self.rect.left < 0:
            self.rect.left = 0

        LEVEL_WIDTH = 3000
        if self.rect.right > LEVEL_WIDTH:
            self.rect.right = LEVEL_WIDTH