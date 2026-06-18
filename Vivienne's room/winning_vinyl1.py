import pygame
from os.path import join

#general set up
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")

fullscreen = False
running = True
clock = pygame.time.Clock()

#import
Sprite = pygame.image.load(join("images", "Player_sprites", "sprite_win.png"))
Vinyl = pygame.image.load(join("images", "items", "vinyl_white.png")).convert_alpha()
#Micheal_Jackson_sound = pygame.mixer.Sound(join("Daniel's Room"/"Audios" "Michael_Jackson-Bad.mp3"))

# use music system for mp3
#pygame.mixer.music.load(join("Daniel's Room", "Audios", "Michael_Jackson-Bad.mp3"))
#pygame.mixer.music.play(-1)  # -1 = loop forever

# Scaling sprtie down size
sprite_size = (300, 570)  # width, height
Sprite = pygame.transform.smoothscale(Sprite, sprite_size)
# scaling vinyal up images
scale_size = (200, 200)  # width, height in pixels
Vinyl = pygame.transform.smoothscale(Vinyl, scale_size)

#center images
screen_width = screen.get_width()
center_x = screen_width // 2
Sprite_rect = Sprite.get_rect(center=(center_x, 400))
Vinyl_rect = Vinyl.get_rect(center=(center_x, 170))

#Rotating Vinyl 
angle = 0

# Main loop
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
    angle = (angle + 1) % 360
    rotated_vinyl = pygame.transform.rotate(Vinyl, angle)
    rotated_rect = rotated_vinyl.get_rect(center=Vinyl_rect.center)

    # Draw
    screen.fill((172, 230, 222))
    screen.blit(Sprite, Sprite_rect)
    screen.blit(rotated_vinyl, rotated_rect)
    
    
    pygame.display.update()

pygame.quit()
