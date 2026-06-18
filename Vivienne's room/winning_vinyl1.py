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
#2quavers
Quaver_p = pygame.image.load(join("images", "musical_notes", "2quavers_pink.png"))
Quaver_pu = pygame.image.load(join("images", "musical_notes", "2quavers_purple.png"))
Quaver_b = pygame.image.load(join("images", "musical_notes", "2quavers_black.png"))
Quaver_r = pygame.image.load(join("images", "musical_notes", "2quavers_red.png"))
Quaver_y = pygame.image.load(join("images", "musical_notes", "2quavers_yellow.png"))
#brief
Breif_b = pygame.image.load(join("images", "musical_notes", "breif_black.png"))
Breif_p = pygame.image.load(join("images", "musical_notes", "breif_pink.png"))
Breif_pu = pygame.image.load(join("images", "musical_notes", "breif_purple.png"))
Breif_r = pygame.image.load(join("images", "musical_notes", "breif_red.png"))
#Quaver
quaver_b = pygame.image.load(join("images", "musical_notes", "quaver_black.png"))
quaver_pu = pygame.image.load(join("images", "musical_notes", "quaver_purple.png"))
quaver_r = pygame.image.load(join("images", "musical_notes", "quaver_red.png"))
quaver_y = pygame.image.load(join("images", "musical_notes", "quaver_yellow.png"))
#triplets
triplets_b = pygame.image.load(join("images", "musical_notes", "triplet_black.png"))
#rest
rest_b = pygame.image.load(join("images", "musical_notes", "rest_pink.png"))
rest_r = pygame.image.load(join("images", "musical_notes", "rest_red.png"))
rest_y = pygame.image.load(join("images", "musical_notes", "rest_yellow.png"))



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
#scaling down musical notes
scale_size = (32, 32)  # width, height in pixels
Quaver_p = pygame.transform.smoothscale(Quaver_p, scale_size)
Quaver_pu = pygame.transform.smoothscale(Quaver_pu, scale_size)
Quaver_b = pygame.transform.smoothscale(Quaver_b, scale_size)
Quaver_r = pygame.transform.smoothscale(Quaver_r, scale_size)
Quaver_y = pygame.transform.smoothscale(Quaver_y, scale_size)
#Breif
Breif_b = pygame.transform.smoothscale(Breif_b, scale_size)
Breif_p = pygame.transform.smoothscale(Breif_p, scale_size)
Breif_pu = pygame.transform.smoothscale(Breif_pu, scale_size)
Breif_r = pygame.transform.smoothscale(Breif_r, scale_size)
quaver_b = pygame.transform.smoothscale(quaver_b, scale_size)
quaver_pu = pygame.transform.smoothscale(quaver_pu, scale_size)
quaver_r = pygame.transform.smoothscale(quaver_r, scale_size)
quaver_y = pygame.transform.smoothscale(quaver_y, scale_size)
#triplets
triplets_b = pygame.transform.smoothscale(triplets_b, scale_size)
#rest
rest_b = pygame.transform.smoothscale(rest_b, scale_size)
rest_r = pygame.transform.smoothscale(rest_r, scale_size)
rest_y = pygame.transform.smoothscale(rest_y, scale_size)

#center images
screen_width = screen.get_width()
center_x = screen_width // 2
Sprite_rect = Sprite.get_rect(center=(center_x, 400))
Vinyl_rect = Vinyl.get_rect(center=(center_x, 170))
Quaver_p_rect  = Quaver_p.get_rect(center=(200, 150))

Breif_b_rect   = Breif_b.get_rect(center=(300, 150))
Breif_p_rect   = Breif_p.get_rect(center=(350, 150))
Breif_pu_rect  = Breif_pu.get_rect(center=(400, 150))
Breif_r_rect   = Breif_r.get_rect(center=(450, 150))

quaver_rect    = quaver_b.get_rect(center=(550, 150))
quaver_pu_rect = quaver_pu.get_rect(center=(600, 150))
quaver_r_rect  = quaver_r.get_rect(center=(650, 150))
quaver_y_rect  = quaver_y.get_rect(center=(700, 150))

triplets_b_rect = triplets_b.get_rect(center=(800, 150))

rest_b_rect    = rest_b.get_rect(center=(900, 150))
rest_r_rect    = rest_r.get_rect(center=(950, 150))
rest_y_rect    = rest_y.get_rect(center=(1000, 150))

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

    # 2 Quavers
    screen.blit(Quaver_p, Quaver_p_rect)

    # Breifs
    screen.blit(Breif_b, Breif_b_rect)
    screen.blit(Breif_p, Breif_p_rect)
    screen.blit(Breif_pu, Breif_pu_rect)
    screen.blit(Breif_r, Breif_r_rect)

    # Quavers
    screen.blit(quaver_b, quaver_rect)
    screen.blit(quaver_pu, quaver_pu_rect)
    screen.blit(quaver_r, quaver_r_rect)
    screen.blit(quaver_y, quaver_y_rect)

    # Triplets
    screen.blit(triplets_b, triplets_b_rect)

    # Rests
    screen.blit(rest_b, rest_b_rect)
    screen.blit(rest_r, rest_r_rect)
    screen.blit(rest_y, rest_y_rect)

    pygame.display.update()
    clock.tick(60)


    pygame.display.update()

pygame.quit()
