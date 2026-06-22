import pygame
from os.path import join, dirname, abspath
from tkinter import font

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(pygame.image.load(r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha(), 1.5)
        self.rect = self.image.get_rect(center=(250, 610))
        self.speed = 5

    # Player walk animations
    walk_forward       = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_back          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_right         = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_left          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-4-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_forward_right = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-5-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_forward_left  = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-6-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_back_right    = [pygame.transform.scale_by(
        pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (2).png"), 0.975) for i in range(1, 6)]
    walk_back_left     = [pygame.transform.scale_by(
        pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (2).png"), 0.975) for i in range(1, 6)]
    
    def update(self):
        # Move
        self.rect.x += self.speed

        # Animate
        self.frame += 0.15
        if self.frame >= len(self.walk_right):
            self.frame = 0

        self.image = self.walk_right[int(self.frame)]

        # Loop
        if self.rect.left > 1280:
            self.rect.right = 0

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
HOME = 0
MAIN_MENU = 1
SETTING = 2

game_state = HOME

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

all_sprites = pygame.sprite.Group()
player = Player(all_sprites)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == HOME:
                game_state = MAIN_MENU

    screen.fill((30, 30, 30))

    if game_state == HOME:
        screen.blit(Background, Background_rect)
        screen.blit(text1, Text_rect1)
        screen.blit(text2, Text_rect2)
        all_sprites.update()
        all_sprites.draw(screen)

    elif game_state == MAIN_MENU:
        screen.fill((0, 100, 200))
        
    

    pygame.display.update()
pygame.quit()