import pygame
from os.path import join
#general set up
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")

fullscreen = False
running = True
class Slider:
    def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int) -> None:
        self.pos = pos
        self.size = size

        self.slider_left_pos = self.pos


#import
Volume_button = pygame.image.load(join("images", "volume.png")).convert_alpha()

#centre buttons
screen_width = screen.get_width()
center_x = screen_width // 2

Volume_rect = Volume_button.get_rect(center=(center_x, 250))

# Main loop
while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if Volume_rect.collidepoint(event.pos):
                print("Volume clicked")
            
               

    #Display images
    screen.blit(Volume_button, Volume_rect)
    
    pygame.display.update()

pygame.quit()
