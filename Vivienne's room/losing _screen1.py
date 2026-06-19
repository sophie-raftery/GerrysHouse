import pygame
from os.path import join

#general set up
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")

fullscreen = False
running = True


#import
Sprite = pygame.image.load(join("images", "Player_sprites", "sprite_lose.png"))
#Micheal_Jackson_sound = pygame.mixer.Sound(join("Daniel's Room"/"Audios" "Michael_Jackson-Bad.mp3"))

# use music system for mp3
#pygame.mixer.music.load(join("Daniel's Room", "Audios", "Michael_Jackson-Bad.mp3"))
#pygame.mixer.music.play(-1)  # -1 = loop forever

# Scaling sprtie down size
sprite_size = (400, 570)  # width, height
Sprite = pygame.transform.smoothscale(Sprite, sprite_size)




#center images
screen_width = screen.get_width()
center_x = screen_width // 2
Sprite_rect = Sprite.get_rect(center=(center_x, 400))




# Main loop
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False
  

    # Draw
    screen.fill((172, 230, 222))
    screen.blit(Sprite, Sprite_rect)
    
    # Notes
   

    
    
    pygame.display.update()
    
pygame.quit()