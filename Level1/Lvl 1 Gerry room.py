"""
Lvl 1 Gerry room.py  – Gerry's bedroom interior level.
Entered via the front door transition from Test_level.py.
"""

import pygame
from os.path import join
from hotbar import Hotbar, Overlay, InventoryItem


# ---------------------------------------------------------------------------
# Player  (same class as Test_level, self-contained per-level copy)
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(
            r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha()
        self.rect  = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction   = pygame.Vector2()
        self.base_speed  = 100
        self.sprint_speed = 200
        self.speed       = self.base_speed
        self.walking     = False
        self.sprinting   = False
        self.current_walk_index      = 0
        self.last_updated_walk_index = pygame.time.get_ticks()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.sprinting = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        self.speed     = self.sprint_speed if self.sprinting else self.base_speed

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.walking = self.direction.x != 0 or self.direction.y != 0
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        d, a, w, s = keys[pygame.K_d], keys[pygame.K_a], keys[pygame.K_w], keys[pygame.K_s]
        if self.walking:
            if   s and not d and not a: self.image = walk_forward[self.current_walk_index]
            elif w and not d and not a: self.image = walk_back[self.current_walk_index]
            elif s and a and not d:     self.image = walk_forward_left[self.current_walk_index]
            elif s and d and not a:     self.image = walk_forward_right[self.current_walk_index]
            elif w and a and not d:     self.image = walk_back_left[self.current_walk_index]
            elif w and d and not a:     self.image = walk_back_right[self.current_walk_index]
            elif d and not a:           self.image = walk_right[self.current_walk_index]
            elif a and not d:           self.image = walk_left[self.current_walk_index]
        else:
            self.current_walk_index = 0
        self._tick_animation()

    def _tick_animation(self):
        now      = pygame.time.get_ticks()
        interval = 100 if self.sprinting else 200
        if now - self.last_updated_walk_index > interval:
            self.last_updated_walk_index = now
            self.current_walk_index = (self.current_walk_index + 1) % len(walk_forward_right)


# ---------------------------------------------------------------------------
# run()  – called by door.load_next_level()
# ---------------------------------------------------------------------------
def run():
    global WINDOW_WIDTH, WINDOW_HEIGHT
    global walk_forward, walk_back, walk_right, walk_left
    global walk_forward_right, walk_forward_left, walk_back_right, walk_back_left

    pygame.init()
    WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gerry's Room")
    clock = pygame.time.Clock()

    # ---- Background --------------------------------------------------------
    bg_raw  = pygame.image.load("images/Gerry's room.png").convert()
    background = pygame.transform.scale(bg_raw, (WINDOW_WIDTH, WINDOW_HEIGHT))

    # ---- Player walk animations --------------------------------------------
    walk_forward       = [pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (1).png") for i in range(1, 5)]
    walk_back          = [pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (1).png") for i in range(1, 5)]
    walk_right         = [pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png") for i in range(1, 5)]
    walk_left          = [pygame.image.load(rf"images\Player_sprites\sprite-4-{i} (1).png") for i in range(1, 5)]
    walk_forward_right = [pygame.image.load(rf"images\Player_sprites\sprite-5-{i} (1).png") for i in range(1, 5)]
    walk_forward_left  = [pygame.image.load(rf"images\Player_sprites\sprite-6-{i} (1).png") for i in range(1, 5)]
    walk_back_right    = [pygame.transform.scale_by(
        pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (2).png"), 0.65) for i in range(1, 6)]
    walk_back_left     = [pygame.transform.scale_by(
        pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (2).png"), 0.65) for i in range(1, 6)]

    # ---- Hotbar / overlay --------------------------------------------------
    overlay = Overlay(Player)

    # ---- Sprites -----------------------------------------------------------
    all_sprites = pygame.sprite.Group()
    player = Player(all_sprites)

    # ---- Fade in -----------------------------------------------------------
    fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surf.fill((0, 0, 0))
    for alpha in range(255, -1, -6):
        display_surface.blit(background, (0, 0))
        all_sprites.draw(display_surface)
        fade_surf.set_alpha(alpha)
        display_surface.blit(fade_surf, (0, 0))
        pygame.display.update()
        clock.tick(60)

    # ---- Game loop ---------------------------------------------------------
    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                overlay.hotbar.handle_keypress(event)
                # TODO: add door / interaction events here

        all_sprites.update(dt)

        display_surface.blit(background, (0, 0))
        all_sprites.draw(display_surface)
        overlay.display(display_surface)
        pygame.display.update()

    pygame.quit()
