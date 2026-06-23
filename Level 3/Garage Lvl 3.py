"""
Garage Lvl 3.py – Garage interior level.
Entered via exit door from Level 3 Garden.
"""

import pygame
import sys
import os
import math
from os.path import join

# ---------------------------------------------------------------------------
# Ensure hotbar.py and door.py (live in Level1) are importable from anywhere
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
            r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha(), 1.5)
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
# Father — walks back and forth in lower garage; pauses at car every 2nd lap
# ---------------------------------------------------------------------------
class Father(pygame.sprite.Sprite):
    SPEED         = 55
    CHASE_SPEED   = 120
    AGRO_RADIUS   = 144          # ~3× player sprite width
    WAYPOINT_DIST = 22
    ANIM_INTERVAL = 200
    FEELER_LEN    = 70
    FEELER_STEPS  = 8
    FEELER_ANGLES = (-35, 0, 35)
    AVOID_WEIGHT  = 2.5
    STUCK_DIST    = 4
    STUCK_CHECK   = 1.5
    CAR_PAUSE_MS  = 6000

    # Back-and-forth route along the lower region of the garage
    PATROL = [
        pygame.Vector2(350, 560),   # far left
        pygame.Vector2(1000, 560),  # far right
    ]
    # Position in front of the car where he stops to look at it
    CAR_STOP = pygame.Vector2(640, 520)

    def __init__(self, groups, player):
        super().__init__(groups)
        self._player  = player
        self._chasing = False
        self._anims = {
            'down':  father_walk_down,
            'up':    father_walk_up,
            'right': father_walk_right,
            'left':  father_walk_left,
        }
        self._facing     = 'right'
        self._frame_idx  = 0
        self._anim_timer = pygame.time.get_ticks()
        self.image = self._anims[self._facing][0]
        self.rect  = self.image.get_rect(center=(int(self.PATROL[0].x), int(self.PATROL[0].y)))
        self.pos   = pygame.Vector2(self.rect.center)

        self._patrol_idx  = 0
        self._waypoint    = pygame.Vector2(self.PATROL[1])
        self._lap_count   = 0          # increments each time he reaches the far right
        self._pausing     = False      # True while stopped at car
        self._pause_timer = 0

        self._last_stuck_check  = pygame.time.get_ticks()
        self._pos_at_last_check = pygame.Vector2(self.pos)

    def _next_patrol_point(self):
        self._patrol_idx = (self._patrol_idx + 1) % len(self.PATROL)
        # Count a lap every time he reaches index 1 (far right)
        if self._patrol_idx == 1:
            self._lap_count += 1
        self._waypoint = pygame.Vector2(self.PATROL[self._patrol_idx])

    def _update_facing(self, direction):
        if abs(direction.x) >= abs(direction.y):
            self._facing = 'left' if direction.x > 0 else 'right'
        else:
            self._facing = 'down' if direction.y > 0 else 'up'

    def _tick_animation(self):
        now    = pygame.time.get_ticks()
        frames = self._anims[self._facing]
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

        # --- Pausing at car — agro disabled while stopped -------------------
        if self._pausing:
            self._chasing = False
            self._facing  = 'up'
            self.image    = self._anims[self._facing][0]
            if now - self._pause_timer >= self.CAR_PAUSE_MS:
                self._pausing = False
                self._waypoint = pygame.Vector2(self.PATROL[self._patrol_idx])
            return

        # --- Agro check -----------------------------------------------------
        player_dist = pygame.Vector2(self._player.rect.center).distance_to(self.pos)
        self._chasing = player_dist <= self.AGRO_RADIUS

        if self._chasing:
            to_player = pygame.Vector2(self._player.rect.center) - self.pos
            if to_player.length() > 0:
                goal_dir = to_player.normalize()
                move_dir = self._compute_steering(goal_dir)
                self._update_facing(move_dir)
                self.pos += move_dir * self.CHASE_SPEED * dt
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                self._push_out_of_obstacles()
            self._tick_animation()
            return
        # --------------------------------------------------------------------

        to_target = self._waypoint - self.pos
        dist = to_target.length()

        if dist <= self.WAYPOINT_DIST or dist == 0:
            if getattr(self, '_heading_to_car', False):
                self._pausing        = True
                self._pause_timer    = now
                self._heading_to_car = False
                self._tick_animation()
                return

            self._next_patrol_point()
            if self._lap_count % 2 == 0 and self._lap_count > 0:
                self._waypoint       = pygame.Vector2(self.CAR_STOP)
                self._lap_count      = 0
                self._heading_to_car = True
            else:
                self._heading_to_car = False
            self._tick_animation()
            return

        goal_dir = to_target.normalize()
        move_dir = self._compute_steering(goal_dir)
        self._update_facing(move_dir)
        self.pos += move_dir * self.SPEED * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self._push_out_of_obstacles()

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
DEBUG_COLLISIONS = True

_WALL_T = 40
COLLISION_RECTS = [
    pygame.Rect(0,              0,    1280, 170),   # top
    pygame.Rect(0,    720 - _WALL_T,  1280, _WALL_T),   # bottom
    pygame.Rect(0,              0,  _WALL_T, 720),      # left
    pygame.Rect(1280 - _WALL_T, 0,  _WALL_T, 720),      # right
    pygame.Rect(0 , 300, 180, 420),
    pygame.Rect(1100, 400, 280, 420),
    pygame.Rect(600, 0, 100, 400),
    pygame.Rect(300, 0, 700, 240),
    pygame.Rect(400, 390, 460, 50)
    
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
# run() – entry point
# ---------------------------------------------------------------------------
def run(incoming_hotbar_slots=None):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    global walk_forward, walk_back, walk_right, walk_left
    global walk_forward_right, walk_forward_left, walk_back_right, walk_back_left
    global father_walk_down, father_walk_up, father_walk_right, father_walk_left

    pygame.init()
    WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gddarage")
    clock = pygame.time.Clock()

    # Background
    background = pygame.image.load("images/garage.png").convert()
    background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # Car — easily adjustable scale and position
    CAR_SCALE = 1.0  # Adjust this to change size
    CAR_POS   = (640, 400)  # Adjust this to change position
    car_img = pygame.image.load("images/Car.png").convert_alpha()
    car_img = pygame.transform.scale_by(car_img, CAR_SCALE)
    car_rect = car_img.get_rect(center=CAR_POS)

    # Player walk animations
    walk_forward       = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_back          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_right         = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_left          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-4-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_forward_right = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-5-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_forward_left  = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-6-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_back_right    = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (2).png"), 0.925) for i in range(1, 6)]
    walk_back_left     = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (2).png"), 0.925) for i in range(1, 6)]

    # Father walk animations (4 directions × 4 frames)
    FATHER_SCALE = 1.5
    father_walk_down  = [pygame.transform.scale_by(pygame.image.load(rf"images\Dad_sprites\sprite-1-{i}.png").convert_alpha(), FATHER_SCALE) for i in range(1, 5)]
    father_walk_up    = [pygame.transform.scale_by(pygame.image.load(rf"images\Dad_sprites\sprite-2-{i}.png").convert_alpha(), FATHER_SCALE) for i in range(1, 5)]
    father_walk_right = [pygame.transform.scale_by(pygame.image.load(rf"images\Dad_sprites\sprite-3-{i}.png").convert_alpha(), FATHER_SCALE) for i in range(1, 5)]
    father_walk_left  = [pygame.transform.scale_by(pygame.image.load(rf"images\Dad_sprites\sprite-4-{i}.png").convert_alpha(), FATHER_SCALE) for i in range(1, 5)]

    # Hotbar
    overlay = Overlay(Player)

    # Restore items from previous level
    if incoming_hotbar_slots:
        for i, item in enumerate(incoming_hotbar_slots):
            overlay.hotbar.slots[i] = item
    elif getattr(shared_state, 'incoming_hotbar_slots', None):
        for i, item in enumerate(shared_state.incoming_hotbar_slots):
            overlay.hotbar.slots[i] = item
        shared_state.incoming_hotbar_slots = None

    # ── Adjustable exit door position and player return spawn ──────────────
    EXIT_DOOR_POS = (116, 180)    # ← move the door here
    RETURN_SPAWN  = (500, 400)   # ← player appears here in Lvl 3 garden on return
    GARAGE_SPAWN  = (120, 245)   # ← player appears here when entering garage from garden

    # Exit door — back to Level 3 garden
    exit_door = Door(
        pos           = EXIT_DOOR_POS,
        target_module = "Level 3/Lvl 3.py",
        image_path    = None,
        size          = (75, 120),
    )

    # Lose door — triggered when father catches the player
    lose_door = Door(
        pos           = (0, 0),
        target_module = "Vivienne's room/losing _screen1.py",
        image_path    = None,
        size          = (1, 1),
    )

    # ---------------------------------------------------------------------------
    # Katy Perry vinyl interaction box
    # ↓↓ Adjust these two lines to reposition / resize the box ↓↓
    VINYL_BOX_POS    = (1125, 225)   # ← world position (x, y)
    VINYL_BOX_SIZE   = (48, 125)     # ← visual size of the box in pixels
    VINYL_BOX_SCALE  = 1.0          # ← scale the box image (1.0 = no change)
    VINYL_BOX_RADIUS = 100          # ← interaction radius in pixels
    # ↑↑ ----------------------------------------------------------------- ↑↑

    _vb_font = pygame.font.SysFont(None, 20)

    class VinylBox:
        def __init__(self):
            self.collected   = False
            self.show_prompt = False
            w = int(VINYL_BOX_SIZE[0] * VINYL_BOX_SCALE)
            h = int(VINYL_BOX_SIZE[1] * VINYL_BOX_SCALE)
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            self.image.fill((200, 60, 200, 210))
            pygame.draw.rect(self.image, (140, 20, 140), self.image.get_rect(), 3)
            # Small vinyl icon
            cx, cy = w // 2, h // 2
            pygame.draw.circle(self.image, (20, 20, 20),   (cx, cy), min(w, h) // 3)
            pygame.draw.circle(self.image, (200, 60, 200), (cx, cy), min(w, h) // 8)
            self.rect = self.image.get_rect(center=VINYL_BOX_POS)
            self._prompt_surf = _vb_font.render("[E] Take vinyl", True, (255, 255, 255))
            self._prompt_shad = _vb_font.render("[E] Take vinyl", True, (0,   0,   0))
            self._done_surf   = _vb_font.render("Got it!",        True, (120, 255, 120))
            self._done_shad   = _vb_font.render("Got it!",        True, (0,   0,   0))

        def update(self, player):
            dist = pygame.Vector2(player.rect.center).distance_to(
                   pygame.Vector2(VINYL_BOX_POS))
            self.show_prompt = dist <= VINYL_BOX_RADIUS

        def interact(self, hotbar):
            if self.collected:
                return False
            self.collected = True
            katie_vinyl = InventoryItem("Katie_Vinyl", "Quest Item",
                                        "images/items/Vinyl_red.png")
            hotbar.add_item_first_free(katie_vinyl)
            return True

        def draw(self, surface):
            if self.show_prompt and not self.collected:
                glow = pygame.Surface((self.rect.width + 30,
                                       self.rect.height + 30), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (220, 80, 220, 70), glow.get_rect())
                surface.blit(glow, glow.get_rect(center=self.rect.center))
            if not self.collected:
                surface.blit(self.image, self.rect)
            if self.show_prompt:
                lbl  = self._done_surf   if self.collected else self._prompt_surf
                shad = self._done_shad   if self.collected else self._prompt_shad
                px = self.rect.centerx - lbl.get_width() // 2
                py = self.rect.top - 24
                surface.blit(shad, (px + 1, py + 1))
                surface.blit(lbl,  (px,     py))

    vinyl_box = VinylBox()

    # Sprites
    all_sprites = pygame.sprite.Group()
    player = Player(all_sprites)
    player.rect.center = GARAGE_SPAWN   # ← spawn position when entering from garden
    father = Father(all_sprites, player)

    # Fade in
    fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surf.fill((0, 0, 0))
    for alpha in range(255, -1, -6):
        display_surface.blit(background, (0, 0))
        display_surface.blit(car_img, car_rect)
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
                        shared_state.incoming_hotbar_slots = list(overlay.hotbar.slots)
                        shared_state.returned_hotbar_slots = None
                        shared_state.return_spawn          = RETURN_SPAWN
                        exit_door.load_next_level()
                    elif vinyl_box.show_prompt:
                        vinyl_box.interact(overlay.hotbar)

        exit_door.update(player)
        vinyl_box.update(player)
        all_sprites.update(dt)
        resolve_collision(player)

        # Father catch — if father touches player while chasing, go to lose screen
        if father._chasing and father.rect.colliderect(player.rect):
            lose_door.transition(display_surface)
            lose_door.load_next_level()
            return

        # Draw — Y-sort each sprite against the car independently
        display_surface.blit(background, (0, 0))
        behind_car  = [s for s in all_sprites if s.rect.bottom < car_rect.centery]
        infront_car = [s for s in all_sprites if s.rect.bottom >= car_rect.centery]
        for sprite in behind_car:
            display_surface.blit(sprite.image, sprite.rect)
        display_surface.blit(car_img, car_rect)
        for sprite in infront_car:
            display_surface.blit(sprite.image, sprite.rect)
        exit_door.draw(display_surface)
        vinyl_box.draw(display_surface)

        if DEBUG_COLLISIONS:
            pulse = int(abs(math.sin(pygame.time.get_ticks() / 300)) * 120 + 30)
            for col_rect in COLLISION_RECTS:
                glow_surf = pygame.Surface((col_rect.width, col_rect.height), pygame.SRCALPHA)
                glow_surf.fill((255, 0, 0, pulse))
                display_surface.blit(glow_surf, col_rect.topleft)
                pygame.draw.rect(display_surface, (255, 0, 0), col_rect, 2)

            # Agro ring — draw only the arc segments not blocked by collision rects
            if not father._pausing:
                agro_r    = Father.AGRO_RADIUS
                cx, cy    = int(father.pos.x), int(father.pos.y)
                SEGMENTS  = 72   # number of rays around the circle
                for i in range(SEGMENTS):
                    angle = 2 * math.pi * i / SEGMENTS
                    dx    = math.cos(angle)
                    dy    = math.sin(angle)
                    # Ray-march: check if this direction is blocked by a collision rect
                    blocked = False
                    for step in range(1, agro_r, 4):
                        px = cx + dx * step
                        py = cy + dy * step
                        for col_rect in COLLISION_RECTS:
                            if col_rect.collidepoint(px, py):
                                blocked = True
                                break
                        if blocked:
                            break
                    if not blocked:
                        end_x = cx + int(dx * agro_r)
                        end_y = cy + int(dy * agro_r)
                        col = (255, 0, 0, min(255, pulse + 80))
                        dot_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
                        dot_surf.fill(col)
                        display_surface.blit(dot_surf, (end_x - 2, end_y - 2))

        overlay.display(display_surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    os.chdir(os.path.join(_HERE, ".."))
    run()
