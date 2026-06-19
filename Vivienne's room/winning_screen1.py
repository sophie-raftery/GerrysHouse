import pygame
from os.path import join
pygame.init()

#general set up
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")

fullscreen = False
running = True
clock = pygame.time.Clock()

# Audio
pygame.mixer.init()
Micheal_Jackson_sound = pygame.mixer.Sound(join("Daniel's Room", "Audios", "bad.mp3"))
Micheal_Jackson_sound.set_volume(9.0)
# Play forever
Micheal_Jackson_sound.play(loops=-1)
#import
Sprite = pygame.image.load(join("images", "Player_sprites", "sprite_win.png"))
Vinyl = pygame.image.load(join("images", "items", "vinyl_white.png")).convert_alpha()
Back_arrow = pygame.image.load(join("images", "buttons", "back arrow.png"))
Forward_arrow = pygame.image.load(join("images", "buttons", "forward arrow.png"))

Quaver_pink = pygame.image.load(join("images", "musical_notes", "2quavers_pink.png"))
Quaver_purple = pygame.image.load(join("images", "musical_notes", "quaver_purple.png"))
Quaver_black = pygame.image.load(join("images", "musical_notes", "quaver_black.png"))
Triplet_red = pygame.image.load(join("images", "musical_notes", "triplet_red.png"))

# Scaling sprtie down size
sprite_size = (300, 570)  # width, height
Sprite = pygame.transform.smoothscale(Sprite, sprite_size)

# scaling vinyal up images
scale_size = (200, 200)  # width, height in pixels
Vinyl = pygame.transform.smoothscale(Vinyl, scale_size)

#scaling down musical notes
note_size = (32, 32)  # width, height in pixels
Quaver_pink = pygame.transform.smoothscale(Quaver_pink, note_size)
Quaver_purple = pygame.transform.smoothscale(Quaver_purple, note_size)
Quaver_black = pygame.transform.smoothscale(Quaver_black, note_size)
Triplet_red = pygame.transform.smoothscale(Triplet_red, note_size)


#center images
screen_width = screen.get_width()
center_x = screen_width // 2
Sprite_rect = Sprite.get_rect(center=(center_x, 400))
Vinyl_rect = Vinyl.get_rect(center=(center_x, 170))
Quaver_pink_rect  = Quaver_pink.get_rect(center=(center_x,70))
Quaver_purple_rect = Quaver_pink.get_rect(center=(center_x-110, 110))
Quaver_black_rect = Quaver_pink.get_rect(center=(center_x+110,110))
Triplet_red_rect = Quaver_pink.get_rect(center=(center_x-110, 230))
Back_arrow_rect = Back_arrow.get_rect(center=(550, 650))
Forward_arrow_rect = Forward_arrow.get_rect(center=(720, 650))


#Rotating Vinyl 
angle = 0

# Main loop
while running:
    music_started = False
    if not music_started:
        Micheal_Jackson_sound.play(loops=-1)
        music_started = True

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
    # Notes
    screen.blit(Quaver_pink, Quaver_pink_rect)
    screen.blit(Quaver_purple, Quaver_purple_rect)
    screen.blit(Quaver_black, Quaver_black_rect)
    screen.blit(Triplet_red, Triplet_red_rect)
    screen.blit(Back_arrow, Back_arrow_rect)
    screen.blit(Forward_arrow, Forward_arrow_rect)

    
    Micheal_Jackson_sound.stop()
    pygame.display.update()
    clock.tick(60)
pygame.quit()