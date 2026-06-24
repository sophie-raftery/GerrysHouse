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
# Bed – uses real bed.png sprite, no interaction
# ---------------------------------------------------------------------------
class Bed:
    # ↓↓ Adjust these to reposition / resize ↓↓
    BED_POS   = (1000, 200)   # ← (x, y) topleft position
    BED_SIZE  = (220, 160)    # ← (width, height)
    # ↑↑ ----------------------------------------------------------------- ↑↑

    def __init__(self):
        raw = pygame.image.load("images/bed.png").convert_alpha()
        self.image = pygame.transform.scale(raw, self.BED_SIZE)
        self.rect  = self.image.get_rect(topleft=self.BED_POS)

    def update(self, player):
        pass   # no interaction

    def draw(self, surface):
        surface.blit(self.image, self.rect)


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
    BG_NORMAL = pygame.transform.scale(
        pygame.image.load("images/Gerry's room.png").convert(),
        (WINDOW_WIDTH, WINDOW_HEIGHT))
    BG_POST = pygame.transform.scale(
        pygame.image.load("images/Gerry's room post.png").convert(),
        (WINDOW_WIDTH, WINDOW_HEIGHT))
    background = BG_NORMAL   # starts on normal background

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
    bed = Bed()

    # ── Vinyl player prop – requires all 3 vinyls, swaps background on use ──
    VINYL_PLAYER_POS    = (213, 540)   # ← position in room
    VINYL_PLAYER_SCALE  = 0.3         # ← size multiplier
    VINYL_PLAYER_RADIUS = 120          # ← interaction range in pixels
    VINYLS_REQUIRED     = {"MJ_Vinyl", "Billy_Vinyl", "Katie_Vinyl"}  # all 3 needed

    def _load_or_placeholder(path, colour):
        if os.path.isfile(path):
            return pygame.image.load(path).convert_alpha()
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        surf.fill(colour)
        return surf

    vp_with_img    = pygame.transform.scale_by(
        _load_or_placeholder("images/vinyl_player(with).png",    (180, 80, 80, 220)), VINYL_PLAYER_SCALE)
    vp_without_img = pygame.transform.scale_by(
        _load_or_placeholder("images/vinyl_player(without).png", (80, 80, 180, 220)), VINYL_PLAYER_SCALE)

    _vp_font = pygame.font.SysFont(None, 20)

    class VinylPlayer:
        def __init__(self):
            self.activated   = False
            self.show_prompt = False
            self.image       = vp_with_img
            self.rect        = self.image.get_rect(center=VINYL_PLAYER_POS)
            self._prompt_surf   = _vp_font.render("[E] Play vinyls (0/3)", True, (255, 255, 255))
            self._prompt_shad   = _vp_font.render("[E] Play vinyls (0/3)", True, (0,   0,   0))
            self._locked_surf   = _vp_font.render("Need all 3 vinyls",     True, (255, 120, 120))
            self._locked_shad   = _vp_font.render("Need all 3 vinyls",     True, (0,   0,   0))
            self._done_surf     = _vp_font.render("Playing!",              True, (120, 255, 120))
            self._done_shad     = _vp_font.render("Playing!",              True, (0,   0,   0))

        def _count_vinyls(self, hotbar):
            return sum(1 for s in hotbar.slots if s and s.name in VINYLS_REQUIRED)

        def _has_all(self, hotbar):
            have = {s.name for s in hotbar.slots if s and s.name in VINYLS_REQUIRED}
            return VINYLS_REQUIRED.issubset(have)

        def update(self, player, hotbar):
            dist = pygame.Vector2(player.rect.center).distance_to(
                   pygame.Vector2(VINYL_PLAYER_POS))
            self.show_prompt = dist <= VINYL_PLAYER_RADIUS
            # Refresh prompt text with live count
            if not self.activated:
                n = self._count_vinyls(hotbar)
                txt = f"[E] Play vinyls ({n}/3)"
                self._prompt_surf = _vp_font.render(txt, True, (255, 255, 255))
                self._prompt_shad = _vp_font.render(txt, True, (0,   0,   0))

        def interact(self, hotbar):
            if self.activated:
                return False
            if not self._has_all(hotbar):
                return False
            self.activated = True
            self.image = vp_without_img
            self.rect  = self.image.get_rect(center=VINYL_PLAYER_POS)
            return True

        def draw(self, surface):
            surface.blit(self.image, self.rect)
            if self.show_prompt:
                glow = pygame.Surface((self.rect.width + 30,
                                       self.rect.height + 30), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (255, 220, 100, 70), glow.get_rect())
                surface.blit(glow, glow.get_rect(center=self.rect.center))
                if self.activated:
                    lbl, shad = self._done_surf, self._done_shad
                else:
                    lbl, shad = self._prompt_surf, self._prompt_shad
                px = self.rect.centerx - lbl.get_width() // 2
                py = self.rect.top - 24
                surface.blit(shad, (px + 1, py + 1))
                surface.blit(lbl,  (px,     py))

    vinyl_player = VinylPlayer()

    _msg_text     = ""
    _msg_timer    = 0
    _MSG_DURATION = 2500
    _msg_font     = pygame.font.SysFont(None, 26)

    # ── Cutscene box – only visible/interactable after vinyls are played ────
    CUTSCENE_BOX_POS    = (65, 400)   # ← position in room
    CUTSCENE_BOX_SCALE  = 4.0          # ← size multiplier (1.0 = 44×44 px)
    CUTSCENE_BOX_RADIUS = 110          # ← interaction range

    _cb_font = pygame.font.SysFont(None, 20)

    class CutsceneBox:
        def __init__(self):
            self.show_prompt = False
            self.triggered   = False
            base_w = int(44 * CUTSCENE_BOX_SCALE)
            base_h = int(44 * CUTSCENE_BOX_SCALE)
            # Invisible surface — glow and prompt shown when nearby
            self.image = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
            self.rect = self.image.get_rect(center=CUTSCENE_BOX_POS)
            self._prompt_surf = _cb_font.render("[E] Watch cutscene", True, (255, 255, 255))
            self._prompt_shad = _cb_font.render("[E] Watch cutscene", True, (0,   0,   0))

        def update(self, player, vinyls_activated):
            if not vinyls_activated:
                self.show_prompt = False
                return
            dist = pygame.Vector2(player.rect.center).distance_to(
                   pygame.Vector2(CUTSCENE_BOX_POS))
            self.show_prompt = dist <= CUTSCENE_BOX_RADIUS

        def draw(self, surface, vinyls_activated):
            if not vinyls_activated:
                return
            if self.show_prompt:
                glow = pygame.Surface((74, 74), pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (100, 200, 255, 70), glow.get_rect())
                surface.blit(glow, glow.get_rect(center=self.rect.center))
            surface.blit(self.image, self.rect)
            if self.show_prompt:
                px = self.rect.centerx - self._prompt_surf.get_width() // 2
                py = self.rect.top - 24
                surface.blit(self._prompt_shad, (px + 1, py + 1))
                surface.blit(self._prompt_surf, (px,     py))

    cutscene_box = CutsceneBox()

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
        vinyl_player.draw(display_surface)
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

                # DEBUG: press O to add all 3 vinyls
                if event.key == pygame.K_o:
                    overlay.hotbar.add_item_first_free(InventoryItem("MJ_Vinyl",    "Quest Item", "images/items/Vinyl_white.png"))
                    overlay.hotbar.add_item_first_free(InventoryItem("Billy_Vinyl", "Quest Item", "images/items/Vinyl_yellow.png"))
                    overlay.hotbar.add_item_first_free(InventoryItem("Katie_Vinyl", "Quest Item", "images/items/Vinyl_red.png"))

                if event.key == pygame.K_e:
                    if exit_door.try_enter(player):
                        exit_door.transition(display_surface)
                        shared_state.returned_hotbar_slots = list(overlay.hotbar.slots)
                        return
                    elif vinyl_player.show_prompt and not vinyl_player.activated:
                        if vinyl_player.interact(overlay.hotbar):
                            background = BG_POST
                        else:
                            _msg_text  = "Need all 3 vinyls: MJ, Billy Joel & Katie Perry"
                            _msg_timer = pygame.time.get_ticks()
                    elif cutscene_box.show_prompt and not cutscene_box.triggered:
                        cutscene_box.triggered = True
                        # Launch cutscene (blocks until finished / skipped)
                        import importlib.util
                        _cs_path = os.path.join(_HERE, '..', 'EndCutScene', 'ending.py')
                        _cs_spec = importlib.util.spec_from_file_location("_ending", _cs_path)
                        _cs_mod  = importlib.util.module_from_spec(_cs_spec)
                        _cs_spec.loader.exec_module(_cs_mod)
                        _cs_mod.run()
                        # Restore display after cutscene
                        display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                        pygame.display.set_caption("Gerry's Room (Level 4)")

        bed.update(player)
        vinyl_player.update(player, overlay.hotbar)
        cutscene_box.update(player, vinyl_player.activated)
        exit_door.update(player)
        all_sprites.update(dt)
        resolve_collision(player)

        # ---- Draw -----------------------------------------------------------
        display_surface.blit(background, (0, 0))
        bed.draw(display_surface)
        vinyl_player.draw(display_surface)
        cutscene_box.draw(display_surface, vinyl_player.activated)
        exit_door.draw(display_surface)
        all_sprites.draw(display_surface)

        if _msg_text and pygame.time.get_ticks() - _msg_timer < _MSG_DURATION:
            lbl  = _msg_font.render(_msg_text, True, (255, 80, 80))
            shad = _msg_font.render(_msg_text, True, (0,   0,   0))
            mx = WINDOW_WIDTH  // 2 - lbl.get_width()  // 2
            my = WINDOW_HEIGHT // 2 - 60
            display_surface.blit(shad, (mx + 1, my + 1))
            display_surface.blit(lbl,  (mx,     my))
        else:
            _msg_text = ""

        overlay.display(display_surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    os.chdir(os.path.join(_HERE, ".."))
    run()
