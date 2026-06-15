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
Play_button = pygame.image.load(join("images", "play button.png")).convert_alpha()
Setting_button = pygame.image.load(join("images", "setting button.png")).convert_alpha()
Exit_button = pygame.image.load(join("images", "exit button.png")).convert_alpha()

#centre buttons
screen_width = screen.get_width()
center_x = screen_width // 2

Play_rect = Play_button.get_rect(center=(center_x, 250))
Settings_rect = Setting_button.get_rect(center=(center_x, 350))
Exit_rect = Exit_button.get_rect(center=(center_x, 450))

# Main loop
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if Play_rect.collidepoint(event.pos):
                print("Play clicked")
                                      
            if Settings_rect.collidepoint(event.pos):
                print("Setting clicked")
                
            if Exit_rect.collidepoint(event.pos):
                pygame.quit()
    # Draw
    screen.fill((30, 30, 30))

    screen.blit(Play_button, Play_rect)
    screen.blit(Setting_button, Settings_rect)
    screen.blit(Exit_button, Exit_rect)
    pygame.display.update()

pygame.quit()
