import pygame
import subprocess
import sys
from os.path import join, abspath, dirname

# ── General setup ────────────────────────────────────────────────────────────
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")

clock = pygame.time.Clock()

# ── Game-state constants ──────────────────────────────────────────────────────
HOME      = 0
MAIN_MENU = 1
# SETTINGS  = 2

game_state = HOME

# ── Fonts & colours ───────────────────────────────────────────────────────────
font1 = pygame.font.SysFont("Comic Sans MS", 50)
font2 = pygame.font.SysFont("Comic Sans MS", 18)
BLACK = (0, 0, 0)

# ── Home-screen assets ────────────────────────────────────────────────────────
Background     = pygame.image.load(join("images", "Background_home.png")).convert_alpha()
Background_rect = Background.get_rect(center=(640, 450))

text1      = font1.render("Welcome to Jarry's House", True, BLACK)
text2      = font2.render("Click anywhere to begin",  True, BLACK)
Text_rect1 = text1.get_rect(center=(640, 200))
Text_rect2 = text2.get_rect(center=(640, 260))

# ── Main-menu assets ──────────────────────────────────────────────────────────
Play_button     = pygame.image.load(join("images", "buttons", "play button.png")).convert_alpha()
Setting_button  = pygame.image.load(join("images", "buttons", "setting button.png")).convert_alpha()
Exit_button     = pygame.image.load(join("images", "buttons", "exit button.png")).convert_alpha()

Play_rect     = Play_button.get_rect(center=(640, 280))
# Settings_rect = Setting_button.get_rect(center=(640, 380))
Exit_rect     = Exit_button.get_rect(center=(640, 480))

# ── Settings assets ───────────────────────────────────────────────────────────
# Volume_button = pygame.image.load(join("images", "buttons", "volume.png")).convert_alpha()
# Back_button   = pygame.image.load(join("images", "buttons", "back arrow.png")).convert_alpha()

# Volume_rect = Volume_button.get_rect(center=(640, 300))
# Back_rect   = Back_button.get_rect(topleft=(30, 30))

# ── Player sprite ─────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        # Load animations after pygame.init() so images decode correctly
        self.walk_right = [
            pygame.transform.scale_by(
                pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png").convert_alpha(),
                1.5
            )
            for i in range(1, 5)
        ]

        self.image  = self.walk_right[0]
        self.rect   = self.image.get_rect(midbottom=(-60, 650))
        self.frame  = 0.0
        self.speed  = 4
        self.active = True   # set False once the player has walked off screen

    def update(self):
        if not self.active:
            return

        # Move right, stop at x = 500
        if self.rect.x < 500:
            self.rect.x += self.speed

            # Animate while walking
            self.frame += 0.15
            if self.frame >= len(self.walk_right):
                self.frame = 0.0
            self.image = self.walk_right[int(self.frame)]
        else:
            self.rect.x = 500
            self.image = self.walk_right[0]  # stand still on first frame


all_sprites = pygame.sprite.Group()
player      = Player(all_sprites)

# ── Main loop ─────────────────────────────────────────────────────────────────
running = True

while running:
    clock.tick(60)

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # HOME → MAIN_MENU on any click
            if game_state == HOME:
                game_state = MAIN_MENU

            # MAIN_MENU button clicks
            elif game_state == MAIN_MENU:
                if Play_rect.collidepoint(event.pos):
                    root_dir    = abspath(join(dirname(abspath(__file__)), ".."))
                    level1_path = join(root_dir, "Level1", "Test_level.py")
                    subprocess.Popen([sys.executable, level1_path], cwd=root_dir)
                    running = False   # close the home screen once the game launches

                # elif Settings_rect.collidepoint(event.pos):
                #     game_state = SETTINGS

                elif Exit_rect.collidepoint(event.pos):
                    running = False

            # SETTINGS button clicks
            # elif game_state == SETTINGS:
            #     if Volume_rect.collidepoint(event.pos):
            #         print("Volume clicked")

            #     elif Back_rect.collidepoint(event.pos):
            #         game_state = MAIN_MENU

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # if game_state == SETTINGS:
                #     game_state = MAIN_MENU
                if game_state == MAIN_MENU:
                    game_state = HOME

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill((30, 30, 30))

    if game_state == HOME:
        screen.blit(Background, Background_rect)
        screen.blit(text1, Text_rect1)
        screen.blit(text2, Text_rect2)
        all_sprites.update()
        all_sprites.draw(screen)

    elif game_state == MAIN_MENU:
        screen.fill((30, 30, 30))
        screen.blit(Play_button,    Play_rect)
        # screen.blit(Setting_button, Settings_rect)
        screen.blit(Exit_button,    Exit_rect)

    # elif game_state == SETTINGS:
    #     screen.fill((30, 30, 30))
    #     screen.blit(Volume_button, Volume_rect)
    #     screen.blit(Back_button,   Back_rect)

    pygame.display.update()

pygame.quit()
