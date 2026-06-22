"""
Lvl 4.py – Garden exterior level (Level 4 version).
Entered via a Door transition or launched directly.
"""

import pygame
import sys
import os
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


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha()
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
            if   s and not d and not a:  self.image = player_walk_forward[self.current_walk_index]
            elif w and not d and not a:  self.image = player_walk_back[self.current_walk_index]
            elif s and a and not d:      self.image = player_walk_forward_left[self.current_walk_index]
            elif s and d and not a:      self.image = player_walk_forward_right[self.current_walk_index]
            elif w and a and not d:      self.image = player_walk_back_left[self.current_walk_index]
            elif w and d and not a:      self.image = player_walk_back_right[self.current_walk_index]
            elif d and not a:            self.image = player_walk_right[self.current_walk_index]
            elif a and not d:            self.image = player_walk_left[self.current_walk_index]
        else:
            self.current_walk_index = 0
        self._tick_animation()

    def _tick_animation(self):
        now      = pygame.time.get_ticks()
        interval = 100 if self.sprinting else 200
        if now - self.last_updated_walk_index > interval:
            self.last_updated_walk_index = now
            self.current_walk_index = (self.current_walk_index + 1) % len(player_walk_forward_right)

    def player_walk_sound(self):
        if self.walking:
            walk_sound.play()
        else:
            walk_sound.stop()


# ---------------------------------------------------------------------------
# Collision rectangles
# ---------------------------------------------------------------------------
DEBUG_COLLISIONS = False
_WALL_T = 40

COLLISION_RECTS = [
    pygame.Rect(0,              0,    1280, _WALL_T),  # top
    pygame.Rect(0,    720 - _WALL_T,  1280, _WALL_T),  # bottom
    pygame.Rect(0,              0,  _WALL_T, 720),     # left
    pygame.Rect(1280 - _WALL_T, 0,  _WALL_T, 720),     # right
    pygame.Rect(910, 5,   450, 350),                   # house
    pygame.Rect(100, 500, 150, 150),                   # dog house
    pygame.Rect(5 ,5, 265, 200 )
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
# run() — called by door.load_next_level() or directly via __main__
# ---------------------------------------------------------------------------
def run(incoming_hotbar_slots=None):
    global WINDOW_WIDTH, WINDOW_HEIGHT
    global player_walk_forward, player_walk_back, player_walk_right, player_walk_left
    global player_walk_forward_right, player_walk_forward_left
    global player_walk_back_right, player_walk_back_left
    global walk_sound

    pygame.init()
    WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Level 4')
    clock = pygame.time.Clock()

    # Background
    background_surf = pygame.image.load("images/garden.png").convert()
    background_surf = pygame.transform.scale(background_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))

    # Scenery
    house_front  = pygame.transform.scale(pygame.image.load("images/jarrys_house.png"), (450, 450))
    dog_house    = pygame.transform.scale(pygame.image.load("images/dogHouse.png"), (150, 150))
    garage_front = pygame.transform.scale(pygame.image.load("images/Garage(out).png"), (300, 300))

    # Player walk animations
    player_walk_forward       = [pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (1).png") for i in range(1, 5)]
    player_walk_back          = [pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (1).png") for i in range(1, 5)]
    player_walk_right         = [pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png") for i in range(1, 5)]
    player_walk_left          = [pygame.image.load(rf"images\Player_sprites\sprite-4-{i} (1).png") for i in range(1, 5)]
    player_walk_forward_right = [pygame.image.load(rf"images\Player_sprites\sprite-5-{i} (1).png") for i in range(1, 5)]
    player_walk_forward_left  = [pygame.image.load(rf"images\Player_sprites\sprite-6-{i} (1).png") for i in range(1, 5)]
    player_walk_back_right    = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (2).png"), 0.65) for i in range(1, 6)]
    player_walk_back_left     = [pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (2).png"), 0.65) for i in range(1, 6)]

    # Hotbar
    overlay = Overlay(Player)

    # Restore items carried in from a previous level
    if incoming_hotbar_slots:
        for i, item in enumerate(incoming_hotbar_slots):
            overlay.hotbar.slots[i] = item

    # Doors
    front_door = Door(
        pos           = (1004, 320),
        target_module = "Level 4/Lvl 4 Gerry room.py",
        image_path    = None,
        size          = (40, 60),
    )
    vinyl_door = Door(
        pos           = (200, 100),
        target_module = "Vivienne's room/winning_screen1.py",
        image_path    = None,
        size          = (50, 70),
    )

    # Sprites
    all_sprites = pygame.sprite.Group()
    player      = Player(all_sprites)

    walk_sound = pygame.mixer.Sound(join("Daniel's Room", "Audios", "Grass footsteps.wav"))
    walk_sound.set_volume(0.9)

    _msg_text     = ""
    _msg_timer    = 0
    _MSG_DURATION = 2500
    _msg_font     = pygame.font.SysFont(None, 28)

    # Fade in
    fade_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surf.fill((0, 0, 0))
    for alpha in range(255, -1, -6):
        display_surface.blit(background_surf, (0, 0))
        display_surface.blit(house_front,     (850, 5))
        display_surface.blit(dog_house,       (100, 500))
        display_surface.blit(garage_front,    (5, 5))
        all_sprites.draw(display_surface)
        front_door.draw(display_surface)
        vinyl_door.draw(display_surface)
        overlay.display(display_surface)
        fade_surf.set_alpha(alpha)
        display_surface.blit(fade_surf, (0, 0))
        pygame.display.update()
        clock.tick(60)

    running = True
    while running:
        dt = clock.tick(100000) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                overlay.hotbar.handle_keypress(event)

                if event.key == pygame.K_e:
                    if front_door.try_enter(player):
                        front_door.transition(display_surface)
                        import shared_state
                        shared_state.returned_hotbar_slots = None
                        walk_sound.stop()
                        front_door.load_next_level()
                        if shared_state.returned_hotbar_slots is not None:
                            for i, item in enumerate(shared_state.returned_hotbar_slots):
                                overlay.hotbar.slots[i] = item
                        player.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                    elif vinyl_door.try_enter(player):
                        vinyl_names = {"MJ_Vinyl", "Billy_Vinyl", "Katie_Vinyl"}
                        if any(s and s.name in vinyl_names for s in overlay.hotbar.slots):
                            vinyl_door.transition(display_surface)
                            walk_sound.stop()
                            vinyl_door.load_next_level()
                        else:
                            _msg_text  = "You need a vinyl record!"
                            _msg_timer = pygame.time.get_ticks()

        front_door.update(player)
        vinyl_door.update(player)
        all_sprites.update(dt)
        resolve_collision(player)

        # Draw
        display_surface.blit(background_surf, (0, 0))
        display_surface.blit(house_front,     (850, 5))
        display_surface.blit(dog_house,       (100, 500))
        display_surface.blit(garage_front,    (5, 5))
        player.player_walk_sound()
        all_sprites.draw(display_surface)
        front_door.draw(display_surface)
        vinyl_door.draw(display_surface)

        if _msg_text and pygame.time.get_ticks() - _msg_timer < _MSG_DURATION:
            _lbl      = _msg_font.render(_msg_text, True, (255, 80, 80))
            _lbl_shad = _msg_font.render(_msg_text, True, (0, 0, 0))
            _mx = front_door.rect.centerx - _lbl.get_width() // 2
            _my = front_door.rect.top - 30
            display_surface.blit(_lbl_shad, (_mx + 1, _my + 1))
            display_surface.blit(_lbl,      (_mx,     _my))
        else:
            _msg_text = ""

        if DEBUG_COLLISIONS:
            for col_rect in COLLISION_RECTS:
                pygame.draw.rect(display_surface, (255, 0, 0), col_rect, 2)

        overlay.display(display_surface)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    os.chdir(os.path.join(_HERE, ".."))
    run()
