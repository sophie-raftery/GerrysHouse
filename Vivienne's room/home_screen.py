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

#import
text1 = font1.render("Welcome to Jarry's House", True, color)
text2 = font2.render("Click anywhere to begin", True, color)

#centre buttons
screen_width = screen.get_width()
center_x = screen_width // 2

Text_rect1= text1.get_rect(center=(center_x, 250))
Text_rect2 = text2.get_rect(center=(center_x, 350))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    text1 = font1.render("Welcome to Jarry's House", True, color)
    text2 = font2.render("Click anywhere to begin", True, color)

    #Display
    screen.fill((30, 30, 30))
    screen.blit(text1,Text_rect1) 
    screen.blit(text2,Text_rect2) 
    pygame.display.update()
pygame.quit()