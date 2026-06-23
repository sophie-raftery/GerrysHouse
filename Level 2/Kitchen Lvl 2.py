"""
Kitchen Lvl 2.py – Kitchen interior level.
Entered via exit door from Level 2 Garden.
"""

import pygame
import sys
import os
import math
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
# Mother — patrol NPC using same logic as Dog from Test_level
# ---------------------------------------------------------------------------
class Mother(pygame.sprite.Sprite):
    SPEED         = 50
    WAYPOINT_DIST = 22
    ANIM_INTERVAL = 200  # ms per frame — shows all 4 frames clearly
    FEELER_LEN    = 70
    FEELER_STEPS  = 8
    FEELER_ANGLES = (-35, 0, 35)
    AVOID_WEIGHT  = 2.5
    STUCK_DIST    = 4
    STUCK_CHECK   = 1.5

    # Four corners of the walkable area (inset from walls/top collision)
    PATROL = [
        pygame.Vector2(150, 280),   # top-left
        pygame.Vector2(1100, 280),  # top-right
        pygame.Vector2(1100, 620),  # bottom-right
        pygame.Vector2(150, 620),   # bottom-left
    ]

    def __init__(self, groups, player):
        super().__init__(groups)
        self._anims = {
            'down':  mother_walk_down,
            'up':    mother_walk_up,
            'right': mother_walk_right,
            'left':  mother_walk_left,
        }
        self._facing     = 'down'
        self._frame_idx  = 0
        self._anim_timer = pygame.time.get_ticks()
        self.image = self._anims[self._facing][0]
        self.rect  = self.image.get_rect(center=(200, 300))
        self.pos   = pygame.Vector2(self.rect.center)
        self._patrol_idx  = 0
        self._waypoint    = pygame.Vector2(self.PATROL[1])
        self._last_stuck_check  = pygame.time.get_ticks()
        self._pos_at_last_check = pygame.Vector2(self.pos)

    def _next_patrol_point(self):
        self._patrol_idx = (self._patrol_idx + 1) % len(self.PATROL)
        self._waypoint   = pygame.Vector2(self.PATROL[self._patrol_idx])

    def _update_facing(self, direction):
        if abs(direction.x) >= abs(direction.y):
            self._facing = 'left' if direction.x > 0 else 'right'
        else:
            self._facing = 'down' if direction.y > 0 else 'up'

    def _tick_animation(self):
        now    = pygame.time.get_ticks()
        frames = self._anims[self._facing]
        # Advance frame every ANIM_INTERVAL ms, cycling through ALL frames 0-3
        while now - self._anim_timer >= self.ANIM_INTERVAL:
            self._anim_timer += self.ANIM_INTERVAL
            self._frame_idx   = (self._frame_idx + 1) % len(frames)
        self.image = frames[self._frame_idx]

    def _point_in_obstacle(self, px, py):
        for col_rect in COLLISION_RECTS:
            if col_rect.collidepoint(px, py):
                return True
        return False

    def _cast_feeler(self, origin, angle_deg, base_dir):
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        fd = pygame.Vector2(base_dir.x * cos_a - base_dir.y * sin_a,
                            base_dir.x * sin_a + base_dir.y * cos_a)
        step_len = self.FEELER_LEN / self.FEELER_STEPS
        for i in range(1, self.FEELER_STEPS + 1):
            px = origin.x + fd.x * step_len * i
            py = origin.y + fd.y * step_len * i
            if self._point_in_obstacle(px, py):
                closeness = 1.0 - (i / self.FEELER_STEPS)
                avoid = pygame.Vector2(-fd.y, fd.x) if angle_deg >= 0 else pygame.Vector2(fd.y, -fd.x)
                return avoid * (closeness + 0.1)
        return pygame.Vector2(0, 0)

    def _compute_steering(self, goal_dir):
        avoidance = pygame.Vector2(0, 0)
        for angle in self.FEELER_ANGLES:
            avoidance += self._cast_feeler(self.pos, angle, goal_dir)
        steering = goal_dir + avoidance * self.AVOID_WEIGHT if avoidance.length() > 0 else goal_dir
        return steering.normalize() if steering.length() > 0 else goal_dir

    def _push_out_of_obstacles(self):
        resolve_collision(self)

    def update(self, dt):
        now = pygame.time.get_ticks()

        to_target = self._waypoint - self.pos
        dist = to_target.length()

        if dist <= self.WAYPOINT_DIST or dist == 0:
            self._next_patrol_point()
            # Still tick animation even when switching waypoints
            self._tick_animation()
            return

        goal_dir = to_target.normalize()
        move_dir = self._compute_steering(goal_dir)
        self._update_facing(move_dir)
        self.pos += move_dir * self.SPEED * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self._push_out_of_obstacles()

        # Stuck detection
        elapsed = (now - self._last_stuck_check) / 1000.0
        if elapsed >= self.STUCK_CHECK:
            moved = (self.pos - self._pos_at_last_check).length()
            if moved < self.STUCK_DIST:
                self._next_patrol_point()
            self._last_stuck_check  = now
            self._pos_at_last_check = pygame.Vector2(self.pos)

        self._tick_animation()


# ---------------------------------------------------------------------------
# Collision rectangles
# ---------------------------------------------------------------------------
DEBUG_COLLISIONS = False

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
    global mother_walk_down, mother_walk_up, mother_walk_right, mother_walk_left

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

    # Mother walk animations
    MOTHER_SCALE = 2
    mother_walk_down  = [pygame.transform.scale_by(pygame.image.load(rf"images\mother_sprites\sprite-1-{i}.png").convert_alpha(), MOTHER_SCALE) for i in range(1, 5)]
    mother_walk_up    = [pygame.transform.scale_by(pygame.image.load(rf"images\mother_sprites\sprite-2-{i}.png").convert_alpha(), MOTHER_SCALE) for i in range(1, 5)]
    mother_walk_right = [pygame.transform.scale_by(pygame.image.load(rf"images\mother_sprites\sprite-3-{i}.png").convert_alpha(), MOTHER_SCALE) for i in range(1, 5)]
    mother_walk_left  = [pygame.transform.scale_by(pygame.image.load(rf"images\mother_sprites\sprite-4-{i}.png").convert_alpha(), MOTHER_SCALE) for i in range(1, 5)]

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
    mother = Mother(all_sprites, player)

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

                # DEBUG: press O to add a vinyl record
                if event.key == pygame.K_o:
                    _dbg_vinyl = InventoryItem("MJ_Vinyl", "Quest Item", "images/items/Vinyl_white.png")
                    overlay.hotbar.add_item_first_free(_dbg_vinyl)

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

        # Y-sort each sprite against the counter independently.
        # Sprites whose feet are above counter centre → behind counter (draw first).
        # Sprites whose feet are at or below counter centre → in front (draw after).
        behind_counter  = [s for s in all_sprites if s.rect.bottom < counter_rect.centery]
        infront_counter = [s for s in all_sprites if s.rect.bottom >= counter_rect.centery]

        for sprite in behind_counter:
            display_surface.blit(sprite.image, sprite.rect)
        display_surface.blit(counter_img, counter_rect)
        for sprite in infront_counter:
            display_surface.blit(sprite.image, sprite.rect)

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