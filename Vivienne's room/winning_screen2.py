"""
winning_screen2.py – Victory screen after returning the vinyl record.
Plays, shows the player sprite and spinning vinyl.
Forward arrow button loads Level 3.
"""

import pygame
import os
import sys
from os.path import join

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.join(_HERE, '..')
_LVL2 = os.path.join(_ROOT, 'Level2')
if _LVL2 not in sys.path:
    sys.path.insert(0, _LVL2)


def run():
    pygame.init()
    pygame.mixer.init()

    WINDOW_SIZE = (1280, 720)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Gerry's House – Level Clear!")
    clock = pygame.time.Clock()

    # Audio 
    music_path = join(_ROOT, "Daniel's Room", "Audios", "Billy Joel.mp3")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(loops=-1)

    # Images 
    Sprite = pygame.image.load(join(_ROOT, "images", "Player_sprites", "sprite_win.png"))
    Vinyl = pygame.image.load(join(_ROOT, "images", "items", "vinyl_yellow.png")).convert_alpha()
    Back_arrow = pygame.image.load(join(_ROOT, "images", "buttons", "back arrow.png"))
    Fwd_arrow = pygame.image.load(join(_ROOT, "images", "buttons", "forward arrow.png"))

    Quaver_pink   = pygame.image.load(join(_ROOT, "images", "musical_notes", "2quavers_pink.png"))
    Quaver_purple = pygame.image.load(join(_ROOT, "images", "musical_notes", "quaver_purple.png"))
    Quaver_black  = pygame.image.load(join(_ROOT, "images", "musical_notes", "quaver_black.png"))
    Triplet_red   = pygame.image.load(join(_ROOT, "images", "musical_notes", "triplet_red.png"))

    # Scale
    Sprite = pygame.transform.smoothscale(Sprite, (250, 470))
    Vinyl = pygame.transform.smoothscale(Vinyl, (150, 150))
    Quaver_pink = pygame.transform.smoothscale(Quaver_pink, (32, 32))
    Quaver_purple = pygame.transform.smoothscale(Quaver_purple, (32, 32))
    Quaver_black = pygame.transform.smoothscale(Quaver_black, (32, 32))
    Triplet_red = pygame.transform.smoothscale(Triplet_red, (32, 32))

    # Layout
    cx = WINDOW_SIZE[0] // 2
    Sprite_rect = Sprite.get_rect(center=(cx, 350))
    Vinyl_rect = Vinyl.get_rect(center=(cx, 170))
    Quaver_pink_rect = Quaver_pink.get_rect(center=(cx, 60))
    Quaver_purple_rect = Quaver_purple.get_rect(center=(cx - 110, 110))
    Quaver_black_rect = Quaver_black.get_rect(center=(cx + 110, 110))
    Triplet_red_rect = Triplet_red.get_rect(center=(cx - 110, 230))
    Back_rect = Back_arrow.get_rect(center=(410, 650))
    Fwd_rect = Fwd_arrow.get_rect(center=(850, 650))

    # Font 
    font_big = pygame.font.SysFont(None, 56)
    font_sub = pygame.font.SysFont(None, 32)
    title = font_big.render("Level Complete!", True, (60, 30, 100))
    title_shd = font_big.render("Level Complete!", True, (0, 0, 0))
    subtitle = font_sub.render("Press to continue to Level 3", True, (255, 255, 255))
    sub_shd = font_sub.render("Press to continue to Level 3", True, (0, 0, 0))

    angle   = 0
    running = True

    # Fade in 
    fade = pygame.Surface(WINDOW_SIZE)
    fade.fill((0, 0, 0))
    for alpha in range(255, -1, -6):
        screen.fill((172, 230, 222))
        screen.blit(Sprite, Sprite_rect)
        screen.blit(Vinyl, Vinyl_rect)
        fade.set_alpha(alpha)
        screen.blit(fade, (0, 0))
        pygame.display.update()
        clock.tick(60)

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if Fwd_rect.collidepoint(event.pos):
                    # Fade out then load Level 3
                    for alpha in range(0, 256, 6):
                        fade.set_alpha(alpha)
                        screen.blit(fade, (0, 0))
                        pygame.display.update()
                        clock.tick(60)
                    pygame.mixer.music.stop()
                    _load_level3()
                    return
                if Back_rect.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    return  # just exit back to caller

        # Spinning vinyl
        angle = (angle + 1) % 360
        rotated_vinyl = pygame.transform.rotate(Vinyl, angle)
        rotated_rect  = rotated_vinyl.get_rect(center=Vinyl_rect.center)

        # Draw
        screen.fill((172, 230, 222))
        screen.blit(Sprite, Sprite_rect)
        screen.blit(rotated_vinyl, rotated_rect)
        screen.blit(Quaver_pink, Quaver_pink_rect)
        screen.blit(Quaver_purple, Quaver_purple_rect)
        screen.blit(Quaver_black, Quaver_black_rect)
        screen.blit(Triplet_red, Triplet_red_rect)

        # Title
        screen.blit(title_shd, (cx - title.get_width() // 2 + 2, 602))
        screen.blit(title, (cx - title.get_width() // 2, 600))
        screen.blit(sub_shd, (cx - subtitle.get_width() // 2 + 1, 661))
        screen.blit(subtitle, (cx - subtitle.get_width() // 2, 660))

        # Buttons — highlight on hover
        mx, my = pygame.mouse.get_pos()
        fwd_img = pygame.transform.scale_by(Fwd_arrow, 1.15) if Fwd_rect.collidepoint(mx, my) else Fwd_arrow
        bck_img = pygame.transform.scale_by(Back_arrow, 1.15) if Back_rect.collidepoint(mx, my) else Back_arrow
        screen.blit(bck_img, Back_rect)
        screen.blit(fwd_img, Fwd_rect)

        pygame.display.update()

    pygame.mixer.music.stop()
    pygame.quit()


def _load_level3():
    """Load Level 3 after the winning screen."""
    import importlib.util
    lvl3_path = os.path.join(_ROOT, "Level 3", "Lvl 3.py")
    spec   = importlib.util.spec_from_file_location("_lvl3", lvl3_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "run"):
        module.run()


if __name__ == "__main__":
    os.chdir(_ROOT)
    run()
