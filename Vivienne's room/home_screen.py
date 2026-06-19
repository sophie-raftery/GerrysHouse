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
color = (0, 0, 0) #black

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
Background = pygame.image.load(join("images", "Background_home.png"))


#centre buttons
screen_width = screen.get_width()
center_x = screen_width // 2

Text_rect1= text1.get_rect(center=(center_x, 200))
Text_rect2 = text2.get_rect(center=(center_x, 250))
Background_rect = Background.get_rect (center=(center_x, 450))


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
    screen.blit(Background, Background_rect)
    screen.blit(text1,Text_rect1) 
    screen.blit(text2,Text_rect2) 
   
    pygame.display.update()
pygame.quit()