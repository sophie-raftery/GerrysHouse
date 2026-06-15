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
        self.speed = 100

        self.heath =  3
        self.walking = False
        self.current_walk_index = 0
        self.last_updated_walk_index = pygame.time.get_ticks()

        self.image = pygame.transform.scale_by(self.image, 1)


    def update(self, dt):

        keys= pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        if int(keys[pygame.K_d]) - int(keys[pygame.K_a]) != 0 or int(keys[pygame.K_s]) - int(keys[pygame.K_w]) != 0:
            self.walking = True

        else:
            self.walking = False
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt


        if self.walking == True and int(keys[pygame.K_s]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_forward[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_back[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_s]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) == 1:
            self.image = player_walk_forward_left[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_s]) == 1 and int(keys[pygame.K_d]) == 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_forward_right[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) == 1:
            self.image = player_walk_back_left[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) == 1 and int(keys[pygame.K_d]) == 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_back_right[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) != 1 and int(keys[pygame.K_d]) == 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_right[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) != 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) == 1:
            self.image = player_walk_left[self.current_walk_index]

        else:
            self.current_walk_index = 0

        self.update_walking_animation()

    def update_walking_animation(self):

        now = pygame.time.get_ticks()
        if now - self.last_updated_walk_index > 200:
            self.last_updated_walk_index = now
            self.current_walk_index = (self.current_walk_index + 1) % len(player_walk_forward_right)


#images
background_img = pygame.image.load("images/garden.png")
player_surf = pygame.image.load("Donncha_room\sprites\sprite-1-1 (1).png")

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

#background image scaled to fit window - sophie
background_surf = pygame.image.load("images/gardenTestingScreenSize.png").convert()
background_surf = pygame.transform.scale(
    background_surf, (WINDOW_WIDTH, WINDOW_HEIGHT)
)

#Lists
player_walk_forward = [pygame.image.load(f"Donncha_room\sprites\sprite-1-{i} (1).png") for i in range (1,5)]
player_walk_back = [pygame.image.load(f"Donncha_room\sprites\sprite-2-{i} (1).png") for i in range (1,5)]
player_walk_right = [pygame.image.load(f"Donncha_room\sprites\sprite-3-{i} (1).png") for i in range (1,5)]
player_walk_left = [pygame.image.load(f"Donncha_room\sprites\sprite-4-{i} (1).png") for i in range (1,5)]
player_walk_forward_right = [pygame.image.load(f"Donncha_room\sprites\sprite-5-{i} (1).png") for i in range (1,5)]
player_walk_forward_left = [pygame.image.load(f"Donncha_room\sprites\sprite-6-{i} (1).png") for i in range (1,5)]
#player_walk_back_left = [pygame.image.load(f"Donncha_room\sprites\sprite-1-{i} (2).png") for i in range (1,5)]
#player_walk_back_right = [pygame.image.load(f"Donncha_room\sprites\sprite-2-{i} (2).png") for i in range (1,5)]



#walking backwards
player_walk_back_right1 = pygame.image.load("Donncha_room\sprites\sprite-1-1 (2).png")
player_walk_back_left1 = pygame.image.load('Donncha_room\sprites\sprite-2-1 (2).png')
player_walk_back_right1 = pygame.transform.scale_by(player_walk_back_right1, 0.65)
player_walk_back_left1 = pygame.transform.scale_by(player_walk_back_left1, 0.65)
player_walk_back_right2 = pygame.image.load("Donncha_room\sprites\sprite-1-2 (2).png")
player_walk_back_left2 = pygame.image.load('Donncha_room\sprites\sprite-2-2 (2).png')
player_walk_back_right2 = pygame.transform.scale_by(player_walk_back_right2, 0.65)
player_walk_back_left2 = pygame.transform.scale_by(player_walk_back_left2, 0.65)
player_walk_back_right3 = pygame.image.load("Donncha_room\sprites\sprite-1-3 (2).png")
player_walk_back_left3 = pygame.image.load('Donncha_room\sprites\sprite-2-3 (2).png')
player_walk_back_right3 = pygame.transform.scale_by(player_walk_back_right3, 0.65)
player_walk_back_left3 = pygame.transform.scale_by(player_walk_back_left3, 0.65)
player_walk_back_right4 = pygame.image.load("Donncha_room\sprites\sprite-1-4 (2).png")
player_walk_back_left4 = pygame.image.load('Donncha_room\sprites\sprite-2-4 (2).png')
player_walk_back_right4 = pygame.transform.scale_by(player_walk_back_right4, 0.65)
player_walk_back_left4 = pygame.transform.scale_by(player_walk_back_left4, 0.65)
player_walk_back_right5 = pygame.image.load("Donncha_room\sprites\sprite-1-5 (2).png")
player_walk_back_left5 = pygame.image.load('Donncha_room\sprites\sprite-2-5 (2).png')
player_walk_back_right5 = pygame.transform.scale_by(player_walk_back_right5, 0.65)
player_walk_back_left5 = pygame.transform.scale_by(player_walk_back_left5, 0.65)

player_walk_back_right = [player_walk_back_left1,player_walk_back_left2,player_walk_back_left3,player_walk_back_left4,player_walk_back_left5]
player_walk_back_left= [player_walk_back_right1,player_walk_back_right2,player_walk_back_right3,player_walk_back_right4,player_walk_back_right5]

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
   # all_sprites.update_walking_animation()
    # draw background image
    display_surface.blit(background_surf, (0, 0))

    all_sprites.draw(display_surface)
    overlay.display(display_surface)
    pygame.display.update()
    
pygame.quit()

