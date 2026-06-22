"""
Lvl 4 Gerry room.py  – Gerry's bedroom interior (Level 4 version).
Entered via the front door from Level 4.
Bed is already in completed state – no mini-game required.
"""

import pygame
import sys
import os

# ---------------------------------------------------------------------------
# Path setup – make Level1 imports (hotbar, door, shared_state) available
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_LVL1 = os.path.join(_HERE, '..', 'Level1')
if _LVL1 not in sys.path:
    sys.path.insert(0, _LVL1)

from hotbar import Hotbar, Overlay, InventoryItem
from door import Door
import shared_state

# ---------------------------------------------------------------------------
# Constants (set inside run() and exposed as globals for class bodies)
# ---------------------------------------------------------------------------
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720

# ---------------------------------------------------------------------------
# Collision rectangles – built inside run() after pygame.init()
# ---------------------------------------------------------------------------
COLLISION_RECTS = []

_WALL_T = 40

def _build_collision_rects():
    """Populate COLLISION_RECTS after pygame is initialised."""
    global COLLISION_RECTS
    COLLISION_RECTS = [
        pygame.Rect(0,                0,           WINDOW_WIDTH,  _WALL_T),   # top
        pygame.Rect(0,  WINDOW_HEIGHT - _WALL_T,   WINDOW_WIDTH,  _WALL_T),   # bottom
        pygame.Rect(0,                0,            _WALL_T,       WINDOW_HEIGHT),  # left
        pygame.Rect(WINDOW_WIDTH - _WALL_T, 0,      _WALL_T,       WINDOW_HEIGHT),  # right
        pygame.Rect(0,    0,  300, 200),   # top-left corner furniture
        pygame.Rect(900,  0,  380, 180),   # top-right corner furniture
        pygame.Rect(500,  0,  200, 120),   # centre-top obstacle
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
# Bed – already completed, just decorative + "Bed made" label
# ---------------------------------------------------------------------------
class Bed:
    INTERACT_RADIUS = 90

    def __init__(self, pos):
        self.pos         = pygame.Vector2(pos)
        self.completed   = True
        self.show_prompt = False

        self.image = pygame.Surface((96, 64), pygame.SRCALPHA)
        self.image.fill((180, 150, 130))
        pygame.draw.rect(self.image, (120, 90, 60), self.image.get_rect(), 4)
        pygame.draw.rect(self.image, (220, 220, 240), pygame.Rect(10, 10, 76, 24))
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        font = pygame.font.SysFont(None, 20)
        self._done_surf = font.render("Bed made", True, (120, 255, 120))
        self._done_shad = font.render("Bed made", True, (0,   0,   0))

    def update(self, player):
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        self.show_prompt = dist <= self.INTERACT_RADIUS

    def draw(self, surface):
        if self.show_prompt:
            glow = pygame.Surface((100, 80), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 220, 100, 70), glow.get_rect())
            surface.blit(glow, glow.get_rect(center=self.rect.center))
        surface.blit(self.image, self.rect)
        if self.show_prompt:
            px = self.rect.centerx - self._done_surf.get_width() // 2
            py = self.rect.top - 22
            surface.blit(self._done_shad, (px + 1, py + 1))
            surface.blit(self._done_surf, (px,     py))


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.transform.scale_by(
            pygame.image.load(r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha(), 1.5)
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
        self.sprinting   = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        self.speed       = self.sprint_speed if self.sprinting else self.base_speed
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        self.walking     = self.direction.x != 0 or self.direction.y != 0
        if self.walking:
            self.direction = self.direction.normalize()
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
# run() – entry point; called by door.load_next_level() from Level 4
# ---------------------------------------------------------------------------
def run(incoming_hotbar_slots=None):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    global walk_forward, walk_back, walk_right, walk_left
    global walk_forward_right, walk_forward_left, walk_back_right, walk_back_left

    pygame.init()
    WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
    _build_collision_rects()

    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Gerry's Room (Level 4)")
    clock = pygame.time.Clock()

    # ---- Background --------------------------------------------------------
    background = pygame.transform.scale(
        pygame.image.load("images/Gerry's room.png").convert(),
        (WINDOW_WIDTH, WINDOW_HEIGHT))

    # ---- Walk animations (2.5× scale to match interior levels) -------------
    walk_forward       = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_back          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_right         = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_left          = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-4-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_forward_right = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-5-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_forward_left  = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-6-{i} (1).png"), 1.5) for i in range(1, 5)]
    walk_back_right    = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (2).png"), 0.975) for i in range(1, 6)]
    walk_back_left     = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (2).png"), 0.975) for i in range(1, 6)]

    # ---- Hotbar ------------------------------------------------------------
    overlay = Overlay(Player)

    # Restore items carried in from Level 4
    if incoming_hotbar_slots:
        for i, item in enumerate(incoming_hotbar_slots):
            overlay.hotbar.slots[i] = item
    elif getattr(shared_state, 'incoming_hotbar_slots', None):
        for i, item in enumerate(shared_state.incoming_hotbar_slots):
            overlay.hotbar.slots[i] = item
        shared_state.incoming_hotbar_slots = None  # consumed
    elif getattr(shared_state, 'returned_hotbar_slots', None):
        for i, item in enumerate(shared_state.returned_hotbar_slots):
            overlay.hotbar.slots[i] = item

    # ---- Room objects -------------------------------------------------------
    bed = Bed(pos=(640, 420))

    # Exit door – uses the standard Door class; just returns to Level 4
    exit_door = Door(
        pos          = (640, 650),
        target_module = "",       # unused – we return instead of load_next_level
        image_path   = None,
        size         = (40, 60),
    )

    # ---- Sprites ------------------------------------------------------------
    all_sprites = pygame.sprite.Group()
    player = Player(all_sprites)

    # ---- Fade in ------------------------------------------------------------
    fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surf.fill((0, 0, 0))
    for alpha in range(255, -1, -6):
        display_surface.blit(background, (0, 0))
        bed.draw(display_surface)
        exit_door.draw(display_surface)
        all_sprites.draw(display_surface)
        overlay.display(display_surface)
        fade_surf.set_alpha(alpha)
        display_surface.blit(fade_surf, (0, 0))
        pygame.display.update()
        clock.tick(60)

    # ---- Game loop ----------------------------------------------------------
    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                overlay.hotbar.handle_keypress(event)

                # DEBUG: press O to add a vinyl record
                if event.key == pygame.K_o:
                    _dbg_vinyl = InventoryItem("MJ_Vinyl", "Quest Item", "images/items/Vinyl_white.png")
                    overlay.hotbar.add_item_first_free(_dbg_vinyl)

                if event.key == pygame.K_e:
                    if exit_door.try_enter(player):
                        # Fade out, save hotbar, return to Level 4's game loop
                        exit_door.transition(display_surface)
                        shared_state.returned_hotbar_slots = list(overlay.hotbar.slots)
                        return   # resumes Level 4 right after load_next_level()

        bed.update(player)
        exit_door.update(player)
        all_sprites.update(dt)
        resolve_collision(player)

        # ---- Draw -----------------------------------------------------------
        display_surface.blit(background, (0, 0))
        bed.draw(display_surface)
        exit_door.draw(display_surface)
        all_sprites.draw(display_surface)
        overlay.display(display_surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    os.chdir(os.path.join(_HERE, ".."))
    run()
