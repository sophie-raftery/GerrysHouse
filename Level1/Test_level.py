import pygame
import math
from os.path import join
from hotbar import Hotbar, Overlay, InventoryItem
from door import Door


DEBUG_COLLISIONS = True
# GroundItem – an item lying on the ground that the player can pick up
class GroundItem(pygame.sprite.Sprite):
    PICKUP_RADIUS = 80

    def __init__(self, groups, inventory_item, pos):
        super().__init__(groups)
        self.inventory_item = inventory_item
        self.image = pygame.transform.scale(inventory_item.img, (32, 36))
        self.rect  = self.image.get_rect(center=pos)
        self._font = pygame.font.SysFont(None, 20)
        self._prompt_surf   = self._font.render("[E] Pick up", True, (255, 255, 255))
        self._prompt_shadow = self._font.render("[E] Pick up", True, (0, 0, 0))
        self.show_prompt = False

    def update(self, dt):
        pass

    def draw(self, surface):
        if self.show_prompt:
            glow_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 100, 60), (25, 25), 22)
            surface.blit(glow_surf, glow_surf.get_rect(center=self.rect.center))
        surface.blit(self.image, self.rect)
        if self.show_prompt:
            px = self.rect.centerx - self._prompt_surf.get_width() // 2
            py = self.rect.top - 20
            surface.blit(self._prompt_shadow, (px + 1, py + 1))
            surface.blit(self._prompt_surf,   (px,     py))


# ---------------------------------------------------------------------------
# DogBowl – accepts the Dog_Bone item; triggers the dog
# ---------------------------------------------------------------------------
class DogBowl:
    INTERACT_RADIUS = 90

    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.has_bone = False
        raw = pygame.image.load("images/Dog_bowl.png").convert_alpha()
        self.bowl_image = pygame.transform.scale(raw, (45, 45))
        raw_full = pygame.image.load("images/Dog_Bowl+Bone.png").convert_alpha()
        self.bowl_full_image = pygame.transform.scale(raw_full, (45, 45))
        self.rect = self.bowl_image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self._font          = pygame.font.SysFont(None, 20)
        self._prompt_surf   = self._font.render("[E] Place bone", True, (255, 255, 255))
        self._prompt_shadow = self._font.render("[E] Place bone", True, (0, 0, 0))
        self._done_surf     = self._font.render("Bone placed!", True, (120, 255, 120))
        self._done_shadow   = self._font.render("Bone placed!", True, (0, 0, 0))
        self.show_prompt = False

    def try_place_bone(self, hotbar):
        if self.has_bone:
            return False
        # Check selected slot first, then all slots
        selected = hotbar.slots[hotbar.selected_slot]
        if selected and selected.name == "Dog_Bone":
            hotbar.slots[hotbar.selected_slot] = None
            self.has_bone = True
            self.bowl_image = self.bowl_full_image
            return True
        for i, slot in enumerate(hotbar.slots):
            if slot and slot.name == "Dog_Bone":
                hotbar.slots[i] = None
                self.has_bone = True
                self.bowl_image = self.bowl_full_image
                return True
        return False

    def draw(self, surface, dog_at_bowl):
        if self.show_prompt and not self.has_bone:
            glow_surf = pygame.Surface((90, 90), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 80, 70), (45, 45), 40)
            surface.blit(glow_surf, glow_surf.get_rect(center=self.rect.center))
        surface.blit(self.bowl_image, self.rect)
        cx = self.rect.centerx
        ty = self.rect.top - 20
        if self.show_prompt and not self.has_bone:
            surface.blit(self._prompt_shadow, (cx - self._prompt_surf.get_width() // 2 + 1, ty + 1))
            surface.blit(self._prompt_surf,   (cx - self._prompt_surf.get_width() // 2,     ty))
        elif self.has_bone and self.show_prompt:
            surface.blit(self._done_shadow, (cx - self._done_surf.get_width() // 2 + 1, ty + 1))
            surface.blit(self._done_surf,   (cx - self._done_surf.get_width() // 2,     ty))


# ---------------------------------------------------------------------------
# DirtMound – dig with a Shovel to reveal a bone
# ---------------------------------------------------------------------------
class DirtMound:
    INTERACT_RADIUS = 80

    def __init__(self, pos, dog_bone_item, dirty_shovel_item):
        self.pos               = pygame.Vector2(pos)
        self.dog_bone_item     = dog_bone_item
        self.dirty_shovel_item = dirty_shovel_item
        self.dug               = False
        raw = pygame.image.load("images/Dirt_Mound.png").convert_alpha()
        self.mound_image = pygame.transform.scale(raw, (80, 60))
        raw_dug = pygame.image.load("images/Dug_mound.png").convert_alpha()
        self.dug_image = pygame.transform.scale(raw_dug, (80, 60))
        self.rect = self.mound_image.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        self._font            = pygame.font.SysFont(None, 20)
        self._prompt_surf     = self._font.render("[E] Dig", True, (255, 255, 255))
        self._prompt_shadow   = self._font.render("[E] Dig", True, (0, 0, 0))
        self._noshovel_surf   = self._font.render("You need a shovel!", True, (255, 120, 120))
        self._noshovel_shadow = self._font.render("You need a shovel!", True, (0, 0, 0))
        self.show_prompt = False
        self._no_shovel  = False

    def try_dig(self, hotbar):
        if self.dug:
            return False
        shovel_slot = None
        if hotbar.slots[hotbar.selected_slot] and hotbar.slots[hotbar.selected_slot].name == "Shovel":
            shovel_slot = hotbar.selected_slot
        else:
            for i, slot in enumerate(hotbar.slots):
                if slot and slot.name == "Shovel":
                    shovel_slot = i
                    break
        if shovel_slot is None:
            self._no_shovel = True
            return False
        hotbar.slots[shovel_slot] = self.dirty_shovel_item
        hotbar.add_item_first_free(self.dog_bone_item)
        self.dug = True
        return True

    def update(self, dt):
        if not self.show_prompt:
            self._no_shovel = False

    def draw(self, surface):
        img = self.dug_image if self.dug else self.mound_image
        if self.show_prompt and not self.dug:
            glow_surf = pygame.Surface((100, 80), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (200, 160, 80, 60), (0, 0, 100, 80))
            surface.blit(glow_surf, glow_surf.get_rect(center=self.rect.center))
        surface.blit(img, self.rect)
        if self.show_prompt and not self.dug:
            cx = self.rect.centerx
            ty = self.rect.top - 20
            if self._no_shovel:
                surface.blit(self._noshovel_shadow, (cx - self._noshovel_surf.get_width() // 2 + 1, ty + 1))
                surface.blit(self._noshovel_surf,   (cx - self._noshovel_surf.get_width() // 2,     ty))
            else:
                surface.blit(self._prompt_shadow, (cx - self._prompt_surf.get_width() // 2 + 1, ty + 1))
                surface.blit(self._prompt_surf,   (cx - self._prompt_surf.get_width() // 2,     ty))
# Player
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
        self.current_walk_index       = 0
        self.last_updated_walk_index  = pygame.time.get_ticks()

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
# Dog
# ---------------------------------------------------------------------------
class Dog(pygame.sprite.Sprite):
    SPEED         = 60
    WAYPOINT_DIST = 22
    ANIM_INTERVAL = 120
    FEELER_LEN    = 70
    FEELER_STEPS  = 8
    FEELER_ANGLES = (-35, 0, 35)
    AVOID_WEIGHT  = 2.5
    STUCK_DIST    = 4
    STUCK_CHECK   = 1.5

    # Patrol stays clear of the bottom-left / dog house area (x<380, y>400)
    PATROL = [
        pygame.Vector2(300, 110),   # top-left (pulled right of far-left edge)
        pygame.Vector2(680, 100),   # top-right
        pygame.Vector2(730, 450),   # right side coming down
        pygame.Vector2(550, 580),   # bottom-right
        pygame.Vector2(350, 570),   # bottom-centre (stops well clear of dog house)
        pygame.Vector2(300, 280),   # rising back up, staying right of dog house
    ]

    def __init__(self, groups, player):
        super().__init__(groups)
        self._anims = {
            'down':  dog_walk_up,
            'up':    dog_walk_down,
            'right': dog_walk_left,
            'left':  dog_walk_right,
        }
        self._facing     = 'down'
        self._frame_idx  = 0
        self._anim_timer = pygame.time.get_ticks()
        self.image = self._anims[self._facing][0]
        self.rect  = self.image.get_rect(center=(301, 111))   # offset from PATROL[0]
        self.pos   = pygame.Vector2(self.rect.center)
        self._patrol_idx  = 0
        self._waypoint    = pygame.Vector2(self.PATROL[1])    # aim at next point immediately
        self._fetching        = False
        self._at_bowl         = False
        self._bowl_pos        = pygame.Vector2(0, 0)
        self._fetch_stage     = 0
        self._fetch_waypoints = []
        self._last_stuck_check  = pygame.time.get_ticks()
        self._pos_at_last_check = pygame.Vector2(self.pos)

    def go_to_bowl(self, bowl_pos):
        if self._at_bowl:
            return
        self._fetching    = True
        self._at_bowl     = False
        self._bowl_pos    = pygame.Vector2(bowl_pos)
        self._fetch_waypoints = [
            pygame.Vector2(420, 400),
            pygame.Vector2(290, 400),
            self._bowl_pos,
        ]
        self._fetch_stage = 0
        self._waypoint    = self._fetch_waypoints[0]

    def _next_patrol_point(self):
        self._patrol_idx = (self._patrol_idx + 1) % len(self.PATROL)
        self._waypoint   = pygame.Vector2(self.PATROL[self._patrol_idx])

    def _update_facing(self, direction):
        if abs(direction.x) >= abs(direction.y):
            self._facing = 'right' if direction.x > 0 else 'left'
        else:
            self._facing = 'down' if direction.y > 0 else 'up'

    def _tick_animation(self):
        now = pygame.time.get_ticks()
        if now - self._anim_timer >= self.ANIM_INTERVAL:
            self._anim_timer = now
            frames = self._anims[self._facing]
            self._frame_idx = (self._frame_idx + 1) % len(frames)
        self.image = self._anims[self._facing][self._frame_idx]


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

        if self._at_bowl:
            self.image = self._anims['down'][0]
            return

        to_target = self._waypoint - self.pos
        dist = to_target.length()

        if dist <= self.WAYPOINT_DIST or dist == 0:
            if self._fetching:
                self._fetch_stage += 1
                if self._fetch_stage < len(self._fetch_waypoints):
                    self._waypoint = self._fetch_waypoints[self._fetch_stage]
                else:
                    self._at_bowl    = True
                    self._fetching   = False
                    self.pos         = pygame.Vector2(self._bowl_pos.x, self._bowl_pos.y - 30)
                    self.rect.center = (int(self.pos.x), int(self.pos.y))
                    self.image       = self._anims['down'][0]
            else:
                self._next_patrol_point()
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
                if self._fetching:
                    self._fetch_stage += 1
                    if self._fetch_stage < len(self._fetch_waypoints):
                        self._waypoint = self._fetch_waypoints[self._fetch_stage]
                    else:
                        self._at_bowl    = True
                        self._fetching   = False
                        self.pos         = pygame.Vector2(self._bowl_pos)
                        self.rect.center = (int(self.pos.x), int(self.pos.y))
                        self.image       = self._anims['down'][0]
                else:
                    self._next_patrol_point()
            self._last_stuck_check  = now
            self._pos_at_last_check = pygame.Vector2(self.pos)

        self._tick_animation()

# Initialisation

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Test level')


# Background
background_surf = pygame.image.load("images/garden.png").convert()
background_surf = pygame.transform.scale(background_surf, (WINDOW_WIDTH, WINDOW_HEIGHT))

# House + dog house
house_front = pygame.transform.scale(
    pygame.image.load("images/jarrys_house.png"), (450, 450))
dog_house = pygame.transform.scale(
    pygame.image.load("images/dogHouse.png"), (150, 150))

# Player walk animations
player_walk_forward       = [pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (1).png") for i in range(1, 5)]
player_walk_back          = [pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (1).png") for i in range(1, 5)]
player_walk_right         = [pygame.image.load(rf"images\Player_sprites\sprite-3-{i} (1).png") for i in range(1, 5)]
player_walk_left          = [pygame.image.load(rf"images\Player_sprites\sprite-4-{i} (1).png") for i in range(1, 5)]
player_walk_forward_right = [pygame.image.load(rf"images\Player_sprites\sprite-5-{i} (1).png") for i in range(1, 5)]
player_walk_forward_left  = [pygame.image.load(rf"images\Player_sprites\sprite-6-{i} (1).png") for i in range(1, 5)]

player_walk_back_right = [
    pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-2-{i} (2).png"), 0.65)
    for i in range(1, 6)]
player_walk_back_left = [
    pygame.transform.scale_by(pygame.image.load(rf"images\Player_sprites\sprite-1-{i} (2).png"), 0.65)
    for i in range(1, 6)]


# Dog sprite animation — 4 frames per direction
DOG_SCALE = 0.225

def _make_outline(surf, colour=(0, 0, 0, 220), thickness=2):
    w, h = surf.get_size()
    outlined = pygame.Surface((w + thickness * 2, h + thickness * 2), pygame.SRCALPHA)
    mask = pygame.mask.from_surface(surf)
    outline_surf = mask.to_surface(setcolor=colour, unsetcolor=(0, 0, 0, 0))
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            outlined.blit(outline_surf, (dx + thickness, dy + thickness))
    outlined.blit(surf, (thickness, thickness))
    return outlined

dog_walk_down  = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-1-{i} (3).png").convert_alpha(), DOG_SCALE)) for i in range(1, 5)]
dog_walk_up    = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-2-{i} (3).png").convert_alpha(), DOG_SCALE)) for i in range(1, 5)]
dog_walk_right = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-3-{i} (2).png").convert_alpha(), DOG_SCALE)) for i in range(1, 5)]
dog_walk_left  = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-4-{i} (2).png").convert_alpha(), DOG_SCALE)) for i in range(1, 5)]

# Hotbar / inventory
overlay = Overlay(Player)

shovel       = InventoryItem("Shovel",       "Tool",       "images/items/Clean_Shovel.png")
dirty_shovel = InventoryItem("Dirty_Shovel", "Tool",       "images/items/Dirty_Shovel.png")
dog_bone     = InventoryItem("Dog_Bone",     "Quest Item", "images/items/Dog_Bone.png")

# Ground items
ground_items_group = pygame.sprite.Group()
ground_shovel = GroundItem(ground_items_group, shovel, (1220, 420))

# World objects
dog_bowl   = DogBowl((290, 580))
dirt_mound = DirtMound((150, 300), dog_bone, dirty_shovel)

# Door — leads to Level 2 (swap target_module when Level 2 exists)
# Positioned at the front door of the house (~920, 390)
front_door = Door(
    pos           = (1004, 320),
    target_module = "Level1/Lvl 1 Gerry room.py",  # file path — supports spaces
    image_path    = None,
    size          = (40, 60),
)

# Sprites
all_sprites = pygame.sprite.Group()
player = Player(all_sprites)
dog    = Dog(all_sprites, player)


# ---------------------------------------------------------------------------
# Collision rectangles (shared by player and dog)
# ---------------------------------------------------------------------------
DEBUG_COLLISIONS = False
_WALL_T = 40

COLLISION_RECTS = [
    # Border walls
    pygame.Rect(0,              0,    1280, _WALL_T),  # top
    pygame.Rect(0,    720 - _WALL_T,  1280, _WALL_T),  # bottom
    pygame.Rect(0,              0,  _WALL_T, 720),     # left
    pygame.Rect(1280 - _WALL_T, 0,  _WALL_T, 720),     # right
    # House — top 350px blocked, bottom 100px (porch) walkable
    pygame.Rect(910, 5,   450, 350),
    # Dog house
    pygame.Rect(100, 500, 150, 150),
]


def resolve_collision(sprite):
    """Push a sprite's rect out of all COLLISION_RECTS using AABB overlap."""
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

walk_sound = pygame.mixer.Sound(join("Daniel's Room", "Audios", "Grass footsteps.wav"))
walk_sound.set_volume(0.9)

clock   = pygame.time.Clock()
running = True

# Timed message (shown near the front door when entry is blocked)
_msg_text    = ""
_msg_timer   = 0
_MSG_DURATION = 2500  # ms
_msg_font    = pygame.font.SysFont(None, 28)

# ---------------------------------------------------------------------------
# Game loop
# ---------------------------------------------------------------------------
while running:
    dt = clock.tick(100000) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            overlay.hotbar.handle_keypress(event)

            if event.key == pygame.K_e:
                mound_dist = pygame.Vector2(player.rect.center).distance_to(dirt_mound.pos)
                bowl_dist  = pygame.Vector2(player.rect.center).distance_to(dog_bowl.pos)

                if front_door.try_enter(player):
                    if not dog_bowl.has_bone:
                        _msg_text  = "You need to distract the dog first!"
                        _msg_timer = pygame.time.get_ticks()
                    else:
                        front_door.transition(display_surface)
                        import shared_state
                        shared_state.returned_hotbar_slots = None  # clear before entering
                        walk_sound.stop()
                        front_door.load_next_level()
                        # Restore hotbar items the player brought back
                        if shared_state.returned_hotbar_slots is not None:
                            for i, item in enumerate(shared_state.returned_hotbar_slots):
                                overlay.hotbar.slots[i] = item
                elif mound_dist <= DirtMound.INTERACT_RADIUS:
                    dirt_mound.try_dig(overlay.hotbar)
                elif bowl_dist <= DogBowl.INTERACT_RADIUS:
                    if dog_bowl.try_place_bone(overlay.hotbar):
                        dog.go_to_bowl(dog_bowl.pos)
                else:
                    for gitem in list(ground_items_group):
                        dist = pygame.Vector2(player.rect.center).distance_to(gitem.rect.center)
                        if dist <= GroundItem.PICKUP_RADIUS:
                            if overlay.hotbar.add_item_first_free(gitem.inventory_item):
                                gitem.kill()
                            break

    # Proximity prompts
    for gitem in ground_items_group:
        gitem.show_prompt = pygame.Vector2(player.rect.center).distance_to(gitem.rect.center) <= GroundItem.PICKUP_RADIUS
    dog_bowl.show_prompt   = pygame.Vector2(player.rect.center).distance_to(dog_bowl.pos)   <= DogBowl.INTERACT_RADIUS
    dirt_mound.show_prompt = pygame.Vector2(player.rect.center).distance_to(dirt_mound.pos) <= DirtMound.INTERACT_RADIUS
    front_door.update(player)

    all_sprites.update(dt)
    ground_items_group.update(dt)
    dirt_mound.update(dt)


    # Collision resolution
    resolve_collision(player)

    if DEBUG_COLLISIONS:
        for col_rect in COLLISION_RECTS:
            pygame.draw.rect(display_surface, (255, 0, 0), col_rect, 2)

    # Draw
    display_surface.blit(background_surf, (0, 0))
    display_surface.blit(house_front,     (850, 5))
    display_surface.blit(dog_house,       (100, 500))
    player.player_walk_sound()
    all_sprites.draw(display_surface)

    for gitem in ground_items_group:
        gitem.draw(display_surface)

    dirt_mound.draw(display_surface)
    dog_bowl.draw(display_surface, dog._at_bowl)
    front_door.draw(display_surface)

    # Draw timed block message near the front door
    if _msg_text and pygame.time.get_ticks() - _msg_timer < _MSG_DURATION:
        _lbl      = _msg_font.render(_msg_text, True, (255, 80, 80))
        _lbl_shad = _msg_font.render(_msg_text, True, (0, 0, 0))
        _mx = front_door.rect.centerx - _lbl.get_width() // 2
        _my = front_door.rect.top - 30
        display_surface.blit(_lbl_shad, (_mx + 1, _my + 1))
        display_surface.blit(_lbl,      (_mx,     _my))
    else:
        _msg_text = ""

    overlay.display(display_surface)
    pygame.display.update()

pygame.quit()
