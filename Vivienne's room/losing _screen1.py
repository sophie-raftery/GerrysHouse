import pygame
import subprocess
import sys
from os.path import join, abspath, dirname

# ── General setup ─────────────────────────────────────────────────────────────
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")
clock = pygame.time.Clock()

# ── Audio ─────────────────────────────────────────────────────────────────────
pygame.mixer.music.load(join("Daniel's Room", "Audios", "loseaudio.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)   # loop until they retry or quit

# ── Assets ────────────────────────────────────────────────────────────────────
Sprite = pygame.transform.smoothscale(
    pygame.image.load(join("images", "Player_sprites", "sprite_lose.png")).convert_alpha(),
    (400, 570)
    )

Retry_button = pygame.image.load(join("images", "buttons", "restart_button.png")).convert_alpha()
Exit_button  = pygame.image.load(join("images", "buttons", "exit button.png")).convert_alpha()

# ── Layout ────────────────────────────────────────────────────────────────────
center_x = screen.get_width() // 2

Sprite_rect = Sprite.get_rect(center=(center_x, 340))
Retry_rect  = Retry_button.get_rect(center=(center_x - 80, 620))
Exit_rect   = Exit_button.get_rect(center=(center_x + 80, 620))

# ── Helpers ───────────────────────────────────────────────────────────────────
def launch_level1():
    """Relaunch Test_level.py from the GerrysHouse root."""
    root_dir    = abspath(join(dirname(abspath(__file__)), ".."))
    level1_path = join(root_dir, "Level1", "Test_level.py")
    pygame.mixer.music.stop()
    subprocess.Popen([sys.executable, level1_path], cwd=root_dir)

# ── Main loop ─────────────────────────────────────────────────────────────────
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if Retry_rect.collidepoint(event.pos):
                launch_level1()
                running = False      # close this screen

            elif Exit_rect.collidepoint(event.pos):
                running = False

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill((172, 230, 222))
    screen.blit(Sprite,        Sprite_rect)
    screen.blit(Retry_button,  Retry_rect)
    screen.blit(Exit_button,   Exit_rect)

    pygame.display.update()

pygame.quit()
