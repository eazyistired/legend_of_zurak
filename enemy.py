import pygame
from tiles import AnimatedTile
from random import randint

class Enemy(AnimatedTile):
    def __init__(self, pos, size, path):
        super().__init__(pos, size, path)
        x, y = pos
        self.rect = self.image.get_rect(bottomleft=(x, y + size))
        self.speed = randint(3, 5)

    def move(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

        self.rect.x += self.speed

    def reverse(self):
        self.speed *= -1

    def update(self, x_shift):
        self.rect.x += x_shift
        self.animate()
        self.move()