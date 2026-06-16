import pygame
import random
from os.path import join
import os
from hotbar import Hotbar, Overlay, InventoryItem

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
    
    def player_walk_sound(self):
        if self.walking:
            walk_sound.play()
        else:
            walk_sound.stop()

#dog class
class Dog(pygame.sprite.Sprite):
    def __init__(self, groups, player):

        super().__init__(groups)
        self.image = dog_down
        self.rect = self.image.get_rect(center=(1000, 420))
           
        #self.player = player
        #self.image = dog_down
        #self.rect = self.image.get_rect(center=(900, 250))
        #self.pos = pygame.Vector2(self.rect.center)
        #self.speed = 110

    def update(self, dt):
        pass
        #direction = pygame.Vector2(self.player.rect.centerx - self.rect.centerx, self.player.rect.centery - self.rect.centery)
        #distance = direction.length()
        #self.pos += direction * self.speed * dt
        #self.rect.center = self.pos
        
        #the dog will chase the player if inside the detection radius
        #DETECTION_RADIUS = 250
        #if 0 < distance < DETECTION_RADIUS:
        #    direction = direction.normalize()
        #    self.pos += direction * self.speed * dt
        #    self.rect.center = self.pos
        
        #if abs(direction.x) > abs(direction.y):
        #    if direction.x > 0:
        #        self.image = dog_right
        #    else:
        #        self.image = dog_left

        #else:
        #    if direction.y > 0:
        #        self.image = dog_down
        #    else:
        #        self.image = dog_up

#images
background_img = pygame.image.load("images/garden.png")
player_surf = pygame.image.load("Donncha_room\sprites\sprite-1-1 (1).png")
house_front = pygame.image.load("images/jarrys_house.png")
#scaling the house image
house_front = pygame.transform.scale(house_front, (450, 450))
dog_house = pygame.image.load("images/dogHouse.png")
#scaling the dog house image
dog_house = pygame.transform.scale(dog_house, (150, 150))

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

#background image scaled to fit window - sophie
background_surf = pygame.image.load("images/garden.png").convert()
background_surf = pygame.transform.scale(
    background_surf, (WINDOW_WIDTH, WINDOW_HEIGHT)
)

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

#dog sprite animation
dog_down = pygame.image.load("images/dogSprite/dog-down.png").convert_alpha()
dog_up = pygame.image.load("images/dogSprite/dog-up.png").convert_alpha()
dog_left = pygame.image.load("images/dogSprite/dog-left.png").convert_alpha()
dog_right = pygame.image.load("images/dogSprite/dog-right.png").convert_alpha()

#down scaling the dog
dog_down = pygame.transform.scale_by(dog_down, 0.15)
dog_up = pygame.transform.scale_by(dog_up, 0.15)
dog_left = pygame.transform.scale_by(dog_left, 0.15)
dog_right = pygame.transform.scale_by(dog_right, 0.15)

# PLAYER = Player.image
# PLAYER.set_colorkey((252, 252, 253),(0,0,95))

#Hotbar
overlay = Overlay(Player)

shovel = InventoryItem("Shovel","Tool","images/items/Clean_Shovel.png")
dirty_shovel = InventoryItem("Dirty_Shovel","Tool","images/items/Dirty_Shovel.png")
dog_bone = InventoryItem("Dog_Bone","Quest Item","images/items/Dog_Bone.png")
mj_vinyl = InventoryItem("MJ_Vinyl","Quest Item","images/items/Vinyl_white.png")
billy_vinyl = InventoryItem("Billy_Vinyl","Quest Item","images/items/Vinyl_yellow.png")
katie_vinyl = InventoryItem("Katie_Vinyl","Quest Item","images/items/Vinyl_red.png")

overlay.hotbar.add_item(dirty_shovel, 0)
overlay.hotbar.add_item(dog_bone, 1)
overlay.hotbar.add_item(mj_vinyl, 2)
overlay.hotbar.add_item(billy_vinyl, 3)
overlay.hotbar.add_item(katie_vinyl, 4)

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT =   1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Test level')
running = True
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player(all_sprites)
dog = Dog(all_sprites, player)

overlay.display(display_surface)
walk_sound = pygame.mixer.Sound(join("Daniel's Room","Audios", "Grass footsteps.wav"))
walk_sound.set_volume(0.9)


while running:
    dt = clock.tick(100000)/1000


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update(dt)
    # all_sprites.update_walking_animation()
    # draw background image
    display_surface.blit(background_surf, (0, 0))
    #draw the house
    display_surface.blit(house_front, (850, 5))
    #draw the dog house
    display_surface.blit(dog_house, (100, 500))
    player.player_walk_sound()
    all_sprites.draw(display_surface)
    overlay.display(display_surface)

    pygame.display.update()
    
pygame.quit()


