import pygame
import random
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('Donncha_room\sprites\sprite-1-1 (1).png').convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        self.heath =  3


    def update(self, dt):

        keys= pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt


#images
player_surf = pygame.image.load("Donncha_room\sprites\sprite-1-1 (1).png")
# PLAYER = Player.image
# PLAYER.set_colorkey((252, 252, 253),(0,0,95))



pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT =   1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Test level')
running = True
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player(all_sprites)

while running:

    dt = clock.tick(100000)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update(dt)
    display_surface.fill("lightGreen")
    all_sprites.draw(display_surface)
    pygame.display.update()

pygame.quit()
