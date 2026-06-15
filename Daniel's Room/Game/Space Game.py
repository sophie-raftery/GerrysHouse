import pygame
from random import randint, uniform
from os.path import join

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/player.png").convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 450

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        self.mask = pygame.mask.from_surface(self.image)
        
        self.normal_surf = self.image.copy()
        self.flash_surf = self.mask.to_surface(unsetcolor= (0,0,0,0), setcolor = (255,255,255,255))
        self.is_flashing = False
        self.flash_time = 0
        self.flash_duration = 150
        self.health = 6
    
    def flash(self):
        self.health -= 1
        self.is_flashing = True
        self.flash_time = pygame.time.get_ticks()
        damage_sound.play()

    def flash_timer(self):
        if self.is_flashing:
            if pygame.time.get_ticks() - self.flash_time >= self.flash_duration:
                self.is_flashing = False

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):

        # Movement Input
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w]) 
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        # Action Input
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()
        self.flash_timer()
        self.image = self.flash_surf if self.is_flashing else self.normal_surf

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()
    
class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(40,80)
        self.rotation= 0
    
    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed*dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation,1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()

    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    global running

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        player.flash()
        if player.health <= 0:
            running = False
    for laser in laser_sprites:
        collision_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True, pygame.sprite.collide_mask)
        if collision_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)            

def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True , (240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH /2 , WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf , text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 640
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Gerry's Rocket")
running = True
clock = pygame.time.Clock()

# Loading in images safely
star_surf = pygame.image.load(join("images", "star.png")).convert_alpha()
laser_surf = pygame.image.load("images/laser.png").convert_alpha()
meteor_surf = pygame.image.load("images/meteor.png").convert_alpha()
font = pygame.font.Font(join("images", "Oxanium-Bold.ttf"),20)
text_surf = font.render("text", True, (240,240,240))
explosion_frames = []
for i in range (21):
    explosion_frames.append(pygame.image.load(join("images","explosion",f"{i}.png")).convert_alpha())

laser_sound = pygame.mixer.Sound(join("audio", "laser.wav"))
laser_sound.set_volume(0.05)
explosion_sound = pygame.mixer.Sound(join("audio", "explosion.wav"))
explosion_sound.set_volume(0.05)
game_music = pygame.mixer.Sound(join("audio", "game_music.wav"))
game_music.set_volume (0)
game_music.play(loops = -1)
damage_sound = pygame.mixer.Sound(join("audio", "Damage.wav"))
damage_sound.set_volume(1)

# Sprite Groups
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

# Spawn Stars using the Sprite Class
for i in range(20):
    Star(all_sprites, star_surf)

# Spawn Player
player = Player(all_sprites)

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event,500)
# Game Loop
while running: 
    # 1. Delta Time
    dt = clock.tick() / 1000

    # 2. SINGLE Event Loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == meteor_event:
            x,y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x,y), (all_sprites, meteor_sprites))

    # 3. Game Logic Update
    all_sprites.update(dt)
    collisions()
    # 4. Drawing
    display_surface.fill("darkgrey")
    all_sprites.draw(display_surface)
    display_score()
    pygame.display.update()

pygame.quit()
