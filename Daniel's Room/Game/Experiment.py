import pygame
import os

pygame.init()

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Test Level")

clock = pygame.time.Clock()

# Folder containing Experiment.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Debug
print("Script folder:", BASE_DIR)

# PLAYER

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        player_path = os.path.join(
            BASE_DIR,
            "..",
            "sprites",
            "sprite-1-1 (1).png"
        )

        self.image = pygame.image.load(player_path).convert_alpha()

        self.rect = self.image.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )

        self.direction = pygame.Vector2()
        self.speed = 300
        self.health = 3

    def update(self, dt):

        keys = pygame.key.get_pressed()

        self.direction.x = (
            int(keys[pygame.K_RIGHT]) -
            int(keys[pygame.K_LEFT])
        )

        self.direction.y = (
            int(keys[pygame.K_DOWN]) -
            int(keys[pygame.K_UP])
        )

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.center += self.direction * self.speed * dt

# HOTBAR

class Hotbar:
    def __init__(self, player):
        self.player = player

        hotbar_path = os.path.join(BASE_DIR,"..","Hotbar","Hotbar.png")

        print("Loading:", hotbar_path)

        self.hotbar_image = pygame.image.load(hotbar_path).convert_alpha()

        self.hotbar_rect = self.hotbar_image.get_rect(topleft= (10,0))

# INVENTORY ITEM

class InventoryItem:
    def __init__(self, name, item_type, img):
        self.name = name
        self.item_type = item_type
        self.img = pygame.image.load(img).convert_alpha()

# OVERLAY

class Overlay:
    def __init__(self, player):
        self.player = player
        self.hotbar = Hotbar(player)

    def display(self, surface):
        surface.blit(self.hotbar.hotbar_image,self.hotbar.hotbar_rect)

all_sprites = pygame.sprite.Group()

player = Player(all_sprites)
overlay = Overlay(player)

running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update(dt)

    display_surface.fill("lightgreen")

    all_sprites.draw(display_surface)

    overlay.display(display_surface)

    pygame.display.flip()

pygame.quit()