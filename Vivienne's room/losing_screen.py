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
background = pygame.image.load(join("images","redbackground.jpg")).convert_alpha()
game_over = pygame.image.load(join("images", "game_over.png")).convert_alpha()
restart_button = pygame.image.load(join("images", "restart_button.png")).convert_alpha()

#Scale button
restart_button = pygame.transform.smoothscale(restart_button, (250, 80))
background = pygame.transform.smoothscale(background, WINDOW_SIZE)

#centre images
game_over_rect = game_over.get_rect(center=(640, 250))
restart_button_rect = restart_button.get_rect(center=(640, 500))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(WINDOW_SIZE)

    
    #Display images
    screen.blit(background, (0, 0)) #background image
    screen.blit(game_over,game_over_rect)
    screen.blit(restart_button, restart_button_rect)    
    pygame.display.flip()
pygame.quit()
 
 