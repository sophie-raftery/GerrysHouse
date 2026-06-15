import pygame
import random
from os.path import join
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('Donncha_room\sprites\sprite-1-1 (1).png').convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        self.heath =  3

        self.image = pygame.transform.scale_by(self.image, 1)


    def update(self, dt):

        keys= pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt


#images
background_img = pygame.image.load("images/garden.png")
background_img = pygame.transform.scale(background_img, (1280, 720))
house_front = pygame.image.load("images/jarrys_house.png")
house_front = pygame.transform.scale(house_front, (450, 450))
dog_house = pygame.image.load("images/dogHouse.png")
dog_house = pygame.transform.scale(dog_house, (150, 150))
player_surf = pygame.image.load("Donncha_room\sprites\sprite-1-1 (1).png")

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

#background image scaled to fit window - sophie
background_surf = pygame.image.load("images/garden.png").convert()
background_surf = pygame.transform.scale(
    background_surf, (WINDOW_WIDTH, WINDOW_HEIGHT)
)
# PLAYER = Player.image
# PLAYER.set_colorkey((252, 252, 253),(0,0,95))

class Hotbar:
    def __init__(self, player):
        self.player = player

        hotbar_path = os.path.join("Daniel's Room","Hotbar","Hotbar.png")

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



pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT =   1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Test level')
running = True
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player(all_sprites)
overlay = Overlay(player)

while running:

    dt = clock.tick(100000)/1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update(dt)

    # draw background image
    display_surface.blit(background_surf, (0, 0))
    
    #draw the house
    display_surface.blit(house_front, (850, 5))
    #draw the dog house
    display_surface.blit(dog_house, (100, 500))

    all_sprites.draw(display_surface)
    overlay.display(display_surface)
    pygame.display.update()
    
pygame.quit()