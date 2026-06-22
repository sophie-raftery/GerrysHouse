"""
Kitchen Lvl 2.py – Kitchen interior level.
Entered via exit door from Level 2 Garden.
"""

import pygame
import sys
import os
from os.path import join

# ---------------------------------------------------------------------------
# Ensure hotbar.py (lives in Level1) is importable from anywhere
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_LVL1 = os.path.join(_HERE, '..', 'Level1')
if _LVL1 not in sys.path:
    sys.path.insert(0, _LVL1)

from hotbar import Hotbar, Overlay, InventoryItem
from door import Door
import shared_state


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(pygame.image.load(
            r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha(), 2.5)
        self.rect  = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction    = pygame.Vector2()
        self.base_speed   = 150
        self.sprint_speed = 300
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
# Collision rectangles
# ---------------------------------------------------------------------------
DEBUG_COLLISIONS = True

_WALL_T = 40
COLLISION_RECTS = [
    pygame.Rect(0,  0, 1280, 220),
    pygame.Rect(0, 720 - _WALL_T,  1280, _WALL_T),
    pygame.Rect(0, 0,  _WALL_T, 720),
    pygame.Rect(1280 - _WALL_T, 0,  _WALL_T, 720),
    pygame.Rect(360 , 460 , 560, 20)
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
    
    # Pixel-perfect counter collision
    if 'counter_mask_data' in globals():
        mask, counter_rect_ref = counter_mask_data
        if sprite.rect.colliderect(counter_rect_ref):
            # Check pixel-perfect collision
            offset_x = sprite.rect.x - counter_rect_ref.x
            offset_y = sprite.rect.y - counter_rect_ref.y
            try:
                if mask.overlap(pygame.mask.from_surface(sprite.image), (offset_x, offset_y)):
                    # Push player out based on overlap direction
                    ox = min(sprite.rect.right - counter_rect_ref.left,
                            counter_rect_ref.right - sprite.rect.left)
                    oy = min(sprite.rect.bottom - counter_rect_ref.top,
                            counter_rect_ref.bottom - sprite.rect.top)
                    if ox < oy:
                        if sprite.rect.centerx < counter_rect_ref.centerx:
                            sprite.rect.right = counter_rect_ref.left
                        else:
                            sprite.rect.left = counter_rect_ref.right
                    else:
                        if sprite.rect.centery < counter_rect_ref.centery:
                            sprite.rect.bottom = counter_rect_ref.top
                        else:
                            sprite.rect.top = counter_rect_ref.bottom
            except:
                pass


# ---------------------------------------------------------------------------
# run() – entry point
# ---------------------------------------------------------------------------
def run(incoming_hotbar_slots=None):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    global walk_forward, walk_back, walk_right, walk_left
    global walk_forward_right, walk_forward_left, walk_back_right, walk_back_left

    pygame.init()
    WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Kitchen")
    clock = pygame.time.Clock()

    # Background
    background = pygame.image.load("images/kitchen.png").convert()
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))

    # Kitchen counter — easily adjustable scale and position
    COUNTER_SCALE = 0.90  # Adjust this to change size
    COUNTER_POS   = (640, 480)  # Adjust this to change position
    counter_img = pygame.image.load("images/kitchen_counter.png").convert_alpha()
    counter_img = pygame.transform.scale_by(counter_img, COUNTER_SCALE)
    counter_rect = counter_img.get_rect(center=COUNTER_POS)
    
    # # Counter front-half collision — tighter corners, better fit
    # counter_collision = pygame.Rect(
    #     counter_rect.left + counter_rect.width // 6,     # Left inset
    #     counter_rect.centery,                            # Start at middle (front half only)
    #     counter_rect.width - (counter_rect.width // 3),  # Narrower width
    #     counter_rect.height // 2                         # Front half height
    # )
    # COLLISION_RECTS.append(counter_collision)

    # Player walk animations
    walk_forward       = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (1).png"), 2.5) for i in range(1, 5)]
    walk_back          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (1).png"), 2.5) for i in range(1, 5)]
    walk_right         = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png"), 2.5) for i in range(1, 5)]
    walk_left          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-4-{i} (1).png"), 2.5) for i in range(1, 5)]
    walk_forward_right = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-5-{i} (1).png"), 2.5) for i in range(1, 5)]
    walk_forward_left  = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-6-{i} (1).png"), 2.5) for i in range(1, 5)]
    walk_back_right    = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (2).png"), 1.625) for i in range(1, 6)]
    walk_back_left     = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (2).png"), 1.625) for i in range(1, 6)]

    # Hotbar
    overlay = Overlay(Player)

    # Restore items from previous level
    if incoming_hotbar_slots:
        for i, item in enumerate(incoming_hotbar_slots):
            overlay.hotbar.slots[i] = item
    elif hasattr(shared_state, 'returned_hotbar_slots') and shared_state.returned_hotbar_slots:
        for i, item in enumerate(shared_state.returned_hotbar_slots):
            overlay.hotbar.slots[i] = item

    # Exit door — back to garden
    exit_door = Door(
        pos           = (640, 650),
        target_module = "Level 2/Lvl 2.py",
        image_path    = None,
        size          = (55, 66),)

    # Sprites
    all_sprites = pygame.sprite.Group()
    player = Player(all_sprites)

    # Fade in
    fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surf.fill((0, 0, 0))
    for alpha in range(255, -1, -6):
        display_surface.blit(background, (0, 0))
        all_sprites.draw(display_surface)
        overlay.display(display_surface)
        fade_surf.set_alpha(alpha)
        display_surface.blit(fade_surf, (0, 0))
        pygame.display.update()
        clock.tick(60)

    # Game loop
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
                    if exit_door.try_enter(player):
                        exit_door.transition(display_surface)
                        # Save hotbar before leaving
                        shared_state.returned_hotbar_slots = list(overlay.hotbar.slots)
                        exit_door.load_next_level()

        exit_door.update(player)
        all_sprites.update(dt)
        resolve_collision(player)

        # Draw
        display_surface.blit(background, (0, 0))

        # Y-sort the counter against the player:
        # If the player's feet (rect.bottom) are above the counter centre → player
        # is "behind" the island, so draw counter on top.
        # If the player's feet are below the counter centre → player has walked
        # in front of the island, so draw counter first (below the player).
        if player.rect.bottom < counter_rect.centery:
            # Player is behind the counter — draw player first, counter on top
            all_sprites.draw(display_surface)
            display_surface.blit(counter_img, counter_rect)
        else:
            # Player is in front of the counter — draw counter first, player on top
            display_surface.blit(counter_img, counter_rect)
            all_sprites.draw(display_surface)

        exit_door.draw(display_surface)

        if DEBUG_COLLISIONS:
            for col_rect in COLLISION_RECTS:
                glow_surf = pygame.Surface((col_rect.width, col_rect.height), pygame.SRCALPHA)
                glow_surf.fill((255, 0, 0, 60))
                display_surface.blit(glow_surf, col_rect.topleft)
                pygame.draw.rect(display_surface, (255, 0, 0), col_rect, 2)

        overlay.display(display_surface)
        pygame.display.update()

    pygame.quit()
#sdegfefafe