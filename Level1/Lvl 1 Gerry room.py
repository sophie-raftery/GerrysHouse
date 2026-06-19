"""
Lvl 1 Gerry room.py  – Gerry's bedroom interior level.
Entered via the front door transition from Test_level.py.
"""

import pygame
import os
from os.path import join
from hotbar import Hotbar, Overlay, InventoryItem
import minesweeper
import shared_state


DEBUG_COLLISIONS = False
walk_sound.stop()
# ---------------------------------------------------------------------------
# Collision rectangles
# ---------------------------------------------------------------------------
_WALL_T = 40
COLLISION_RECTS = [
    pygame.Rect(0,  0, 1280, 200),
    pygame.Rect(0, 720 - _WALL_T,  1280, _WALL_T),
    pygame.Rect(0, 0,  _WALL_T, 720),
    pygame.Rect(1280 - _WALL_T, 0,  _WALL_T, 720),
    pygame.Rect(0,   0,   300, 200),
    pygame.Rect(900, 0,   380, 180),
    pygame.Rect(500, 0,   200, 120),
]
 
def resolve_collision(sprite):
    for col_rect in COLLISION_RECTS:
        if not sprite.rect.colliderect(col_rect):
            continue
        ox = min(sprite.rect.right  - col_rect.left,
                 col_rect.right - sprite.rect.left)
        oy = min(sprite.rect.bottom - col_rect.top,
                 col_rect.bottom - sprite.rect.top)
        if ox < oy:
            if sprite.rect.centerx < col_rect.centerx:
                sprite.rect.right = col_rect.left
            else:
                sprite.rect.left  = col_rect.right
        else:
            if sprite.rect.centery < col_rect.centery:
                sprite.rect.bottom = col_rect.top
            else:
                sprite.rect.top    = col_rect.bottom


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# InteractableBox  – a box that launches the minesweeper mini-game
# ---------------------------------------------------------------------------
class InteractableBox:
    INTERACT_RADIUS = 90

    def __init__(self, pos):
        self.pos       = pygame.Vector2(pos)
        self.completed = False
        self.show_prompt = False

        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.image.fill((160, 110, 50))
        pygame.draw.rect(self.image, (100, 60, 20), self.image.get_rect(), 3)
        pygame.draw.rect(self.image, (220, 180, 60), (18, 22, 12, 10))
        pygame.draw.arc(self.image, (220, 180, 60),
                        pygame.Rect(18, 15, 12, 14), 0, 3.14159, 3)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        font = pygame.font.SysFont(None, 20)
        self._prompt      = font.render("[E] Open",  True, (255, 255, 255))
        self._prompt_shad = font.render("[E] Open",  True, (0, 0, 0))
        self._done        = font.render("Cleared!",  True, (120, 255, 120))
        self._done_shad   = font.render("Cleared!",  True, (0, 0, 0))

    def update(self, player):
        self.show_prompt = (
            pygame.Vector2(player.rect.center).distance_to(self.pos) <= self.INTERACT_RADIUS
            and not self.completed
        )

    def draw(self, surface):
        if self.show_prompt:
            glow = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 220, 100, 70), glow.get_rect())
            surface.blit(glow, glow.get_rect(center=self.rect.center))
        surface.blit(self.image, self.rect)
        if self.show_prompt:
            lbl  = self._done      if self.completed else self._prompt
            shad = self._done_shad if self.completed else self._prompt_shad
            px = self.rect.centerx - lbl.get_width() // 2
            py = self.rect.top - 22
            surface.blit(shad, (px + 1, py + 1))
            surface.blit(lbl,  (px,     py))


# ---------------------------------------------------------------------------
# MakeBed  – shows messy_bed, launches minesweeper on [E], swaps to clean bed
# ---------------------------------------------------------------------------
class MakeBed:
    INTERACT_RADIUS = 110

    def __init__(self, pos, size=(220, 160)):
        self.pos       = pygame.Vector2(pos)
        self.made      = False
        self.show_prompt = False

        raw_messy = pygame.image.load("images/messy_bed.png").convert_alpha()
        raw_clean = pygame.image.load("images/bed.png").convert_alpha()
        self._messy_img = pygame.transform.scale(raw_messy, size)
        self._clean_img = pygame.transform.scale(raw_clean, size)

        self.rect = self._messy_img.get_rect(topleft=(int(self.pos.x), int(self.pos.y)))

        font = pygame.font.SysFont(None, 20)
        self._prompt      = font.render("[E] Make bed",  True, (255, 255, 255))
        self._prompt_shad = font.render("[E] Make bed",  True, (0, 0, 0))
        self._done        = font.render("Bed made!",     True, (120, 255, 120))
        self._done_shad   = font.render("Bed made!",     True, (0, 0, 0))

    @property
    def image(self):
        return self._clean_img if self.made else self._messy_img

    def update(self, player):
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        self.show_prompt = dist <= self.INTERACT_RADIUS and not self.made

    def draw(self, surface):
        if self.show_prompt:
            glow = pygame.Surface((self.rect.width + 30, self.rect.height + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 220, 100, 60), glow.get_rect())
            surface.blit(glow, glow.get_rect(center=self.rect.center))
        surface.blit(self.image, self.rect)
        if self.show_prompt:
            lbl  = self._done      if self.made else self._prompt
            shad = self._done_shad if self.made else self._prompt_shad
            px = self.rect.centerx - lbl.get_width() // 2
            py = self.rect.top - 22
            surface.blit(shad, (px + 1, py + 1))
            surface.blit(lbl,  (px,     py))

# ---------------------------------------------------------------------------
# ExitDoor  – requires a vinyl + key; returns to Test_level
# ---------------------------------------------------------------------------
class ExitDoor:
    INTERACT_RADIUS = 180

    def __init__(self, pos):
        self.pos         = pygame.Vector2(pos)
        self.show_prompt = False
        self._unlocked   = False
        self.image = pygame.Surface((200, 120), pygame.SRCALPHA)
        self.image.fill((140, 90, 50, 230))
        pygame.draw.rect(self.image, (80, 80, 10), self.image.get_rect(), 3)
        pygame.draw.circle(self.image, (220, 180, 60), (34, 34), 5)
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        font = pygame.font.SysFont(None, 20)
        self._open_s  = font.render("[E] Exit",         True, (255, 255, 255))
        self._open_sh = font.render("[E] Exit",         True, (0, 0, 0))
        self._lock_s  = font.render("Need vinyl + key", True, (255, 120, 120))
        self._lock_sh = font.render("Need vinyl + key", True, (0, 0, 0))

    def _check(self, hotbar):
        vinyl_names = {"MJ_Vinyl", "Billy_Vinyl", "Katie_Vinyl"}
        hv = any(s and s.name in vinyl_names for s in hotbar.slots)
        hk = any(s and s.name == "Room_Key"   for s in hotbar.slots)
        return hv and hk

    def update(self, player, hotbar):
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        self.show_prompt = dist <= self.INTERACT_RADIUS
        self._unlocked   = self._check(hotbar)

    def try_exit(self, hotbar):
        return self._check(hotbar)

    def draw(self, surface):
        if self.show_prompt:
            col  = (100, 255, 100, 70) if self._unlocked else (255, 100, 100, 70)
            glow = pygame.Surface((70, 80), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, col, glow.get_rect())
            surface.blit(glow, glow.get_rect(center=self.rect.center))
        # Door image intentionally not drawn — invisible but hitbox is still active
        if self.show_prompt:
            lbl  = self._open_s  if self._unlocked else self._lock_s
            shad = self._open_sh if self._unlocked else self._lock_sh
            px = self.rect.centerx - lbl.get_width() // 2
            py = self.rect.top - 22
            surface.blit(shad, (px + 1, py + 1))
            surface.blit(lbl,  (px,     py))


# Hotbar state is exported via shared_state.returned_hotbar_slots


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(pygame.image.load(
            r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha(), 1.5)
        self.rect  = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction    = pygame.Vector2()
        self.base_speed   = 100
        self.sprint_speed = 200
        self.speed        = self.base_speed
        self.walking      = False
        self.sprinting    = False
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
        now = pygame.time.get_ticks()
        interval = 100 if self.sprinting else 200
        if now - self.last_updated_walk_index > interval:
            self.last_updated_walk_index = now
            self.current_walk_index = (self.current_walk_index + 1) % len(walk_forward_right)


# ---------------------------------------------------------------------------
# Helper — try to load an image, return a coloured placeholder on failure
# ---------------------------------------------------------------------------
def _load_or_placeholder(path, fallback_color):
    if os.path.isfile(path):
        return pygame.image.load(path).convert_alpha()
    # Placeholder coloured surface
    surf = pygame.Surface((64, 64), pygame.SRCALPHA)
    surf.fill(fallback_color)
    return surf


# ---------------------------------------------------------------------------
# run()  – entry point called by door.load_next_level()
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
    background = pygame.transform.scale(
        pygame.image.load("images/Gerry's room.png").convert(),
        (WINDOW_WIDTH, WINDOW_HEIGHT))

    # ---- Bed (messy → clean via minesweeper) --------------------------------
    make_bed = MakeBed(pos=(1000, 200), size=(220, 160))
    # Collision only covers the bottom 60px of the bed (footboard area)
    COLLISION_RECTS.append(pygame.Rect(1060, 200, 100, 60))

    # ---- Player walk animations --------------------------------------------
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

    # ---- Minesweeper number images -----------------------------------------
    # Swap these paths once you have the real art assets.
    # 1 = Gerry's sock, 2 = Pringles can, 3 = magazine
    number_images = {
        1: _load_or_placeholder("images/Gerrys_Sock.png",      (200, 200, 100)),
        2: _load_or_placeholder("images/Pringles _Can.png",    (200, 80,  20)),
        3: _load_or_placeholder("images/Gerrys_Magazine.png",  (50,  120, 200)),
    }

    # ---- Inventory items ---------------------------------------------------
    mj_vinyl    = InventoryItem("MJ_Vinyl",    "Quest Item", "images/items/Vinyl_white.png")
    billy_vinyl = InventoryItem("Billy_Vinyl", "Quest Item", "images/items/Vinyl_yellow.png")
    katie_vinyl = InventoryItem("Katie_Vinyl", "Quest Item", "images/items/Vinyl_red.png")
    room_key    = InventoryItem("Room_Key",    "Key Item",   "images/Key.png")
    reward_vinyl = mj_vinyl

    # ---- Hotbar ------------------------------------------------------------
    overlay = Overlay(Player)

    # ---- World objects -----------------------------------------------------
    key_box   = InteractableBox(pos=(190, 230))   # top-left box gives the key
    exit_door = ExitDoor(pos=(770, 140))           # upper-middle of the room

    # ---- Sprites -----------------------------------------------------------
    all_sprites = pygame.sprite.Group()
    player = Player(all_sprites)

    # ---- Fade in -----------------------------------------------------------
    fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surf.fill((0, 0, 0))
    for alpha in range(255, -1, -6):
        display_surface.blit(background, (0, 0))
        make_bed.draw(display_surface)
        key_box.draw(display_surface)
        all_sprites.draw(display_surface)
        exit_door.draw(display_surface)
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

                if event.key == pygame.K_e:
                    ppos = pygame.Vector2(player.rect.center)

                    # Make bed
                    if ppos.distance_to(make_bed.pos) <= MakeBed.INTERACT_RADIUS and not make_bed.made:
                        won = minesweeper.run(
                            parent_surface = display_surface,
                            number_images  = number_images,
                        )
                        if won:
                            make_bed.made = True
                            overlay.hotbar.add_item_first_free(reward_vinyl)

                    # Key box — gives room key on completion
                    elif ppos.distance_to(key_box.pos) <= InteractableBox.INTERACT_RADIUS and not key_box.completed:
                        won = minesweeper.run(
                            parent_surface = display_surface,
                            number_images  = number_images,
                        )
                        if won:
                            key_box.completed = True
                            overlay.hotbar.add_item_first_free(room_key)

                    # Exit door — needs vinyl + key
                    elif ppos.distance_to(exit_door.pos) <= ExitDoor.INTERACT_RADIUS:
                        if exit_door.try_exit(overlay.hotbar):
                            # Fade out then hand control back to Test_level
                            fade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
                            fade.fill((0, 0, 0))
                            for alpha in range(0, 256, 6):
                                display_surface.blit(background, (0, 0))
                                make_bed.draw(display_surface)
                                key_box.draw(display_surface)
                                exit_door.draw(display_surface)
                                all_sprites.draw(display_surface)
                                overlay.display(display_surface)
                                fade.set_alpha(alpha)
                                display_surface.blit(fade, (0, 0))
                                pygame.display.update()
                                clock.tick(60)
                            # Export hotbar so Test_level can restore it
                            shared_state.returned_hotbar_slots = list(overlay.hotbar.slots)
                            import sys
                            sys.modules.pop('_next_level', None)
                            return

        make_bed.update(player)
        key_box.update(player)
        exit_door.update(player, overlay.hotbar)
        all_sprites.update(dt)

        display_surface.blit(background, (0, 0))
        make_bed.draw(display_surface)
        key_box.draw(display_surface)
        exit_door.draw(display_surface)
        all_sprites.draw(display_surface)
        overlay.display(display_surface)
        pygame.display.update()
        resolve_collision(player)

    pygame.quit()
