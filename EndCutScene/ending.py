"""
ending.py – Fish cutscene. Call run() to play it.
"""

import pygame
import os
from os.path import join

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, '..')


class FishCutscene:

    def __init__(self):
        self.active = True
        self.timer  = 0
        self.stage  = 0
        self.font   = pygame.font.Font(None, 45)

        self.dialogue = [
            "Patrick?",
            "Is that you??",
            "No...",
            "It can't be..."
        ]

        def _load(rel):
            return pygame.image.load(os.path.join(_ROOT, rel)).convert_alpha()

        self.jarry_neutral = pygame.transform.scale_by(_load("images/Player_sprites/sprite_cutscene_neutral.png"), 0.5)
        self.jarry_sad     = pygame.transform.scale_by(_load("images/Player_sprites/sprite_cutscene_sad.png"),     0.5)
        self.jarry_grief   = pygame.transform.scale_by(_load("images/Player_sprites/sprite_cutscene_grief.png"),   0.5)
        self.fishbowl      = pygame.transform.scale_by(_load("images/fishBowl.png"),   1.5)
        self.patrick       = pygame.transform.scale_by(_load("images/patrickFish.png"), 0.5)

    def update(self, dt):
        self.timer += dt
        if self.timer >= 3:
            self.timer = 0
            self.stage += 1
        if self.stage >= len(self.dialogue):
            self.active = False

    def draw(self, screen):
        screen.fill((0, 0, 0))

        jarry = self.jarry_neutral if self.stage == 0 else (
                self.jarry_sad if self.stage < 3 else self.jarry_grief)

        screen.blit(jarry,         (500, 60))
        screen.blit(self.fishbowl, (280, 60))
        screen.blit(self.patrick,  (560, 230))

        if self.stage < len(self.dialogue):
            text = self.font.render(self.dialogue[self.stage], True, (255, 255, 255))
            screen.blit(text, (420, 650))


def run():
    """Play the cutscene, blocking until it finishes. Safe to call from any level."""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Jarry's House")
    clock = pygame.time.Clock()

    cutscene = FishCutscene()

    while cutscene.active:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                return   # skip on any key press
        cutscene.update(dt)
        cutscene.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    os.chdir(_ROOT)
    run()
    pygame.quit()
