import pygame
from os.path import join, dirname, abspath
from tkinter import font

#general set up
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")

font1 = pygame.font.SysFont("Comic Sans MS", 50)
font2 = pygame.font.SysFont("Comic Sans MS", 15)
color = (225, 225, 225) #white

fullscreen = False
running = True

#switching betweeen pages
#HOME = 0
#MAIN_MENU = 1
#SETTING = 2

#game_state = HOME

#import
text1 = font1.render("Welcome to Jarry's House", True, color)
text2 = font2.render("Click anywhere to begin", True, color)
Home_image = pygame.image.load(join("images", "jarrys_house.png")).convert_alpha() 
Ground = pygame.image.load(join("images", "ground.png")).convert_alpha() 


#centre buttons
tile_width = Ground.get_width()
screen_width = screen.get_width()
center_x = screen_width // 2

Text_rect1= text1.get_rect(center=(center_x, 350))
Text_rect2 = text2.get_rect(center=(center_x, 450))
Ground_rect1 = Ground.get_rect(center=(tile_width // 2, 700))
Ground_rect2 = Ground.get_rect(center=(tile_width // 2 + tile_width, 700))
Ground_rect3 = Ground.get_rect(center=(tile_width // 2 + 2 * tile_width, 700))
Home_image_rect = Home_image.get_rect()
Home_image_rect.left = 5     # 20 pixels from left edge
Home_image_rect.centery = screen.get_height() // 2

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #if game_state == HOME:
        #elif game_state == MAIN_MENU:
        
    
    text1 = font1.render("Welcome to Jarry's House", True, color)
    text2 = font2.render("Click anywhere to begin", True, color)

    #Display
    screen.fill((30, 30, 30))
    screen.blit(text1,Text_rect1) 
    screen.blit(text2,Text_rect2) 
    screen.blit(Home_image, Home_image_rect)
    screen.blit(Ground, Ground_rect1)
    screen.blit(Ground, Ground_rect2)
    screen.blit(Ground, Ground_rect3)
    pygame.display.update()
pygame.quit()