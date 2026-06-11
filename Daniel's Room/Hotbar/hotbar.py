import pygame

class Hotbar:
    def __init__(self, player):
        self.player = player
        self.hotbar_image = pygame.transform.scale(pygame.image.load("#location of image hotbar")(500,64))

        self.hotbar_rect = self.hotbar_image.get_rect(center=((pygame.display.get_window_size()[0]/2, pygame.display.get_window_size()[1]-30)))
        