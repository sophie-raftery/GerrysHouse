import pygame

class Overlay:
    def __init__(self, player):
        self.player = player
        self.hotbar = Hotbar(player)

    def display(self, surface):
        surface.blit(self.hotbar.hotbar_image, self.hotbar.hotbar_rect)


    """ WHEN GAME STARTS RUN SELF>OVERLAYE SELF.PLAYER
    AND SELF.OVERLAY.DISPLAY(Game.manager.screen) IN THE MAIN GAME LOOP """