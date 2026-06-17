import pygame
import random
import math
from os.path import join
import os
from hotbar import Hotbar, Overlay, InventoryItem


# GroundItem – an item lying on the ground that the player can pick up

class GroundItem(pygame.sprite.Sprite):
    PICKUP_RADIUS = 80   # pixels – how close the player must be to pick up
    BOB_SPEED     = 2.5  # how fast the item bobs up and down
    BOB_HEIGHT    = 5    # pixels of vertical travel

    def __init__(self, groups, inventory_item, pos):
        super().__init__(groups)
        self.inventory_item = inventory_item

        # Scale the item image for display on the ground
        self.base_image = pygame.transform.scale(inventory_item.img, (32, 36))
        self.image = self.base_image.copy()
        self.rect  = self.image.get_rect(center=pos)

        # Bobbing state
        self._bob_offset = 0.0
        self._bob_timer  = random.uniform(0, math.pi * 2)  # random phase

        # Prompt font (created once, reused every frame)
        self._font = pygame.font.SysFont(None, 20)
        self._prompt_surf   = self._font.render("[E] Pick up", True, (255, 255, 255))
        self._prompt_shadow = self._font.render("[E] Pick up", True, (0, 0, 0))

        self.show_prompt = False   # set True by the main loop when player is near

    def update(self, dt):
        self._bob_timer += self.BOB_SPEED * dt
        self._bob_offset = math.sin(self._bob_timer) * self.BOB_HEIGHT
        # Keep rect in place; drawing offset handled in draw()

    def draw(self, surface):
        """Call this manually after all_sprites.draw() so the item draws on top."""
        draw_pos = (self.rect.centerx, self.rect.centery + int(self._bob_offset))

        # Subtle glow ring when the player is close enough to pick up
        if self.show_prompt:
            glow_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 255, 100, 60), (25, 25), 22)
            surface.blit(glow_surf, glow_surf.get_rect(center=draw_pos))

        # Item image
        surface.blit(self.base_image, self.base_image.get_rect(center=draw_pos))

        # "[E] Pick up" prompt above the item
        if self.show_prompt:
            px = draw_pos[0] - self._prompt_surf.get_width() // 2
            py = draw_pos[1] - 34
            surface.blit(self._prompt_shadow, (px + 1, py + 1))
            surface.blit(self._prompt_surf,   (px,     py))


# ---------------------------------------------------------------------------
# DogBowl – a placed object in the world; accepts the Dog_Bone item
# ---------------------------------------------------------------------------
class DogBowl:
    INTERACT_RADIUS = 90  # pixels

    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.has_bone = False

        # Bowl image
        raw = pygame.image.load("images/Dog_bowl.png").convert_alpha()
        self.bowl_image = pygame.transform.scale(raw, (45, 45))
        self.rect = self.bowl_image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # Bone thumbnail to draw inside the bowl once placed
        raw_bone = pygame.image.load("images/items/Dog_Bone.png").convert_alpha()
        self.bone_image = pygame.transform.scale(raw_bone, (20, 20))

        # Prompt font
        self._font          = pygame.font.SysFont(None, 20)
        self._prompt_surf   = self._font.render("[E] Place bone", True, (255, 255, 255))
        self._prompt_shadow = self._font.render("[E] Place bone", True, (0, 0, 0))
        self._done_surf     = self._font.render("Bone placed!", True, (120, 255, 120))
        self._done_shadow   = self._font.render("Bone placed!", True, (0, 0, 0))

        self.show_prompt = False  # set by main loop each frame

    # ------------------------------------------------------------------
    def try_place_bone(self, hotbar):
        """
        Check the selected hotbar slot first, then any slot, for a Dog_Bone.
        Removes it and marks the bowl as filled. Returns True on success.
        """
        if self.has_bone:
            return False

        # Check selected slot first
        selected = hotbar.slots[hotbar.selected_slot]
        if selected and selected.name == "Dog_Bone":
            hotbar.slots[hotbar.selected_slot] = None
            self.has_bone = True
            return True

        # Fallback: check all slots
        for i, slot in enumerate(hotbar.slots):
            if slot and slot.name == "Dog_Bone":
                hotbar.slots[i] = None
                self.has_bone = True
                return True

        return False

    # ------------------------------------------------------------------
    def draw(self, surface):
        # Glow when player is close and bone not yet placed
        if self.show_prompt and not self.has_bone:
            glow_surf = pygame.Surface((90, 90), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 80, 70), (45, 45), 40)
            surface.blit(glow_surf, glow_surf.get_rect(center=self.rect.center))

        # Bowl
        surface.blit(self.bowl_image, self.rect)

        # Bone sitting in the bowl
        if self.has_bone:
            bone_rect = self.bone_image.get_rect(center=(self.rect.centerx, self.rect.centery + 4))
            surface.blit(self.bone_image, bone_rect)

        # Prompt text
        cx = self.rect.centerx
        ty = self.rect.top - 20
        if self.show_prompt and not self.has_bone:
            surface.blit(self._prompt_shadow, (cx - self._prompt_surf.get_width() // 2 + 1, ty + 1))
            surface.blit(self._prompt_surf,   (cx - self._prompt_surf.get_width() // 2,     ty))
        elif self.has_bone and self.show_prompt:
            surface.blit(self._done_shadow, (cx - self._done_surf.get_width() // 2 + 1, ty + 1))
            surface.blit(self._done_surf,   (cx - self._done_surf.get_width() // 2,     ty))


# ---------------------------------------------------------------------------
# DirtMound – can be dug with a Shovel to reveal a bone
# ---------------------------------------------------------------------------
class DirtMound:
    INTERACT_RADIUS = 80  # pixels

    def __init__(self, pos, dog_bone_item, dirty_shovel_item):
        self.pos            = pygame.Vector2(pos)
        self.dog_bone_item  = dog_bone_item      # InventoryItem to add on dig
        self.dirty_shovel_item = dirty_shovel_item  # InventoryItem to replace shovel with
        self.dug            = False              # True after the player has dug it

        raw = pygame.image.load("images/Dirt_Mound.png").convert_alpha()
        self.mound_image = pygame.transform.scale(raw, (80, 60))
        # Real dug mound image
        raw_dug = pygame.image.load("images/Dug_mound.png").convert_alpha()
        self.dug_image = pygame.transform.scale(raw_dug, (80, 60))

        self.rect = self.mound_image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        self._font           = pygame.font.SysFont(None, 20)
        self._prompt_surf    = self._font.render("[E] Dig", True, (255, 255, 255))
        self._prompt_shadow  = self._font.render("[E] Dig", True, (0, 0, 0))
        self._noshovel_surf  = self._font.render("Need a shovel!", True, (255, 120, 120))
        self._noshovel_shadow= self._font.render("Need a shovel!", True, (0, 0, 0))
        self._done_surf      = self._font.render("Already dug.", True, (180, 180, 180))
        self._done_shadow    = self._font.render("Already dug.", True, (0, 0, 0))

        self.show_prompt   = False
        self._warn_timer   = 0   # seconds to show "Need a shovel!" warning

    # ------------------------------------------------------------------
    def try_dig(self, hotbar):
        """
        Requires a clean Shovel in the hotbar.
        On success: adds Dog_Bone to hotbar, replaces Shovel with Dirty_Shovel,
        marks mound as dug.  Returns True on success.
        """
        if self.dug:
            return False

        # Find a clean Shovel – check selected slot first, then all slots
        shovel_slot = None
        if hotbar.slots[hotbar.selected_slot] and hotbar.slots[hotbar.selected_slot].name == "Shovel":
            shovel_slot = hotbar.selected_slot
        else:
            for i, slot in enumerate(hotbar.slots):
                if slot and slot.name == "Shovel":
                    shovel_slot = i
                    break

        if shovel_slot is None:
            self._warn_timer = 2.0  # show warning for 2 s
            return False

        # Replace clean shovel with dirty shovel in the same slot
        hotbar.slots[shovel_slot] = self.dirty_shovel_item
        # Add bone to hotbar
        hotbar.add_item_first_free(self.dog_bone_item)
        self.dug = True
        return True

    # ------------------------------------------------------------------
    def update(self, dt):
        if self._warn_timer > 0:
            self._warn_timer -= dt

    # ------------------------------------------------------------------
    def draw(self, surface):
        img = self.dug_image if self.dug else self.mound_image

        # Glow when player is close and mound not yet dug
        if self.show_prompt and not self.dug:
            glow_surf = pygame.Surface((100, 80), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (200, 160, 80, 60), (0, 0, 100, 80))
            surface.blit(glow_surf, glow_surf.get_rect(center=self.rect.center))

        surface.blit(img, self.rect)

        cx = self.rect.centerx
        ty = self.rect.top - 20

        if self.show_prompt:
            if self.dug:
                pass  # no prompt after digging – mound is spent
            elif self._warn_timer > 0:
                surface.blit(self._noshovel_shadow, (cx - self._noshovel_surf.get_width() // 2 + 1, ty + 1))
                surface.blit(self._noshovel_surf,   (cx - self._noshovel_surf.get_width() // 2,     ty))
            else:
                surface.blit(self._prompt_shadow, (cx - self._prompt_surf.get_width() // 2 + 1, ty + 1))
                surface.blit(self._prompt_surf,   (cx - self._prompt_surf.get_width() // 2,     ty))


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('images\Player_sprites\sprite-1-1 (1).png').convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.base_speed   = 100
        self.sprint_speed = 200
        self.speed = self.base_speed

        self.heath =  3
        self.walking = False
        self.sprinting = False
        self.current_walk_index = 0
        self.last_updated_walk_index = pygame.time.get_ticks()

        self.image = pygame.transform.scale_by(self.image, 1)

    def update(self, dt):

        keys= pygame.key.get_pressed()
        recent_keys = pygame.key.get_just_pressed()

        # Sprint when shift is held
        self.sprinting = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        self.speed = self.sprint_speed if self.sprinting else self.base_speed

        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        if int(keys[pygame.K_d]) - int(keys[pygame.K_a]) != 0 or int(keys[pygame.K_s]) - int(keys[pygame.K_w]) != 0:
            self.walking = True

        else:
            self.walking = False
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt


        if self.walking == True and int(keys[pygame.K_s]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_forward[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_back[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_s]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) == 1:
            self.image = player_walk_forward_left[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_s]) == 1 and int(keys[pygame.K_d]) == 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_forward_right[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) == 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) == 1:
            self.image = player_walk_back_left[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) == 1 and int(keys[pygame.K_d]) == 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_back_right[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) != 1 and int(keys[pygame.K_d]) == 1 and int(keys[pygame.K_a]) != 1:
            self.image = player_walk_right[self.current_walk_index]
        elif self.walking == True and int(keys[pygame.K_w]) != 1 and int(keys[pygame.K_d]) != 1 and int(keys[pygame.K_a]) == 1:
            self.image = player_walk_left[self.current_walk_index]

        else:
            self.current_walk_index = 0

        self.update_walking_animation()

    def update_walking_animation(self):
        now = pygame.time.get_ticks()
        interval = 100 if self.sprinting else 200  # faster frames when sprinting
        if now - self.last_updated_walk_index > interval:
            self.last_updated_walk_index = now
            self.current_walk_index = (self.current_walk_index + 1) % len(player_walk_forward_right)
    
    def player_walk_sound(self):
        if self.walking:
            walk_sound.play()
        else:
            walk_sound.stop()

#dog class
class Dog(pygame.sprite.Sprite):
    SPEED         = 60     # pixels per second
    WAYPOINT_DIST = 22     # pixels — "arrived" threshold
    ANIM_INTERVAL = 120    # ms per animation frame

    # Feeler (obstacle sensing) settings
    FEELER_LEN    = 70     # how far ahead to look (px)
    FEELER_STEPS  = 8      # sample points along each feeler
    FEELER_ANGLES = (-35, 0, 35)   # degrees left, centre, right

    # Avoidance strength relative to goal steering
    AVOID_WEIGHT  = 2.5

    # Roaming bounds
    ROAM_X = (80,  1200)
    ROAM_Y = (80,  660)

    PAUSE_MIN = 500
    PAUSE_MAX = 2500

    # Stuck detection
    STUCK_DIST    = 4      # px moved threshold per check
    STUCK_CHECK   = 1.5    # seconds between stuck checks

    def __init__(self, groups, player):
        super().__init__(groups)

        self._anims = {
            'down':  dog_walk_up,
            'up':    dog_walk_down,
            'right': dog_walk_left,
            'left':  dog_walk_right,
        }
        self._facing    = 'down'
        self._frame_idx = 0
        self._anim_timer = pygame.time.get_ticks()

        self.image = self._anims[self._facing][0]
        self.rect  = self.image.get_rect(center=(600, 400))
        self.pos   = pygame.Vector2(self.rect.center)

        self._waypoint    = self._pick_waypoint()
        self._pausing     = False
        self._pause_until = 0

        self._fetching    = False
        self._at_bowl     = False
        self._bowl_pos    = pygame.Vector2(0, 0)
        self._fetch_stage = 0

        # Stuck detection
        self._last_stuck_check = pygame.time.get_ticks()
        self._pos_at_last_check = pygame.Vector2(self.pos)

    # ------------------------------------------------------------------
    def go_to_bowl(self, bowl_pos):
        self._fetching  = True
        self._at_bowl   = False
        self._pausing   = False
        # Route via a waypoint on the LEFT side of the dog house before the bowl.
        # Dog house topleft is (100, 500), opaque area starts ~x=119.
        # Guide point: just left of the dog house and level with its top.
        self._waypoint       = pygame.Vector2(85, 560)   # left-side guide point
        self._bowl_pos       = pygame.Vector2(bowl_pos)  # final destination
        self._fetch_stage    = 0   # 0 = heading to guide, 1 = heading to bowl

    # ------------------------------------------------------------------
    def _pick_waypoint(self):
        return pygame.Vector2(
            random.randint(self.ROAM_X[0], self.ROAM_X[1]),
            random.randint(self.ROAM_Y[0], self.ROAM_Y[1])
        )

    # ------------------------------------------------------------------
    def _update_facing(self, direction):
        if abs(direction.x) >= abs(direction.y):
            self._facing = 'right' if direction.x > 0 else 'left'
        else:
            self._facing = 'down' if direction.y > 0 else 'up'

    # ------------------------------------------------------------------
    def _tick_animation(self):
        now = pygame.time.get_ticks()
        if now - self._anim_timer >= self.ANIM_INTERVAL:
            self._anim_timer = now
            frames = self._anims[self._facing]
            self._frame_idx = (self._frame_idx + 1) % len(frames)
        self.image = self._anims[self._facing][self._frame_idx]

    # ------------------------------------------------------------------
    def _point_in_obstacle(self, px, py):
        """Return True if world point (px,py) overlaps any building mask."""
        for obj_mask, obj_pos in collision_masks:
            lx = int(px - obj_pos.x)
            ly = int(py - obj_pos.y)
            mw, mh = obj_mask.get_size()
            if 0 <= lx < mw and 0 <= ly < mh:
                if obj_mask.get_at((lx, ly)):
                    return True
        return False

    # ------------------------------------------------------------------
    def _cast_feeler(self, origin, angle_deg, base_dir):
        """
        Cast a feeler from origin in base_dir rotated by angle_deg.
        Returns an avoidance vector (perpendicular to feeler, scaled by
        proximity) or zero vector if nothing hit.
        """
        rad    = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        # Rotate base_dir by angle
        fx = base_dir.x * cos_a - base_dir.y * sin_a
        fy = base_dir.x * sin_a + base_dir.y * cos_a
        feeler_dir = pygame.Vector2(fx, fy)

        step_len = self.FEELER_LEN / self.FEELER_STEPS
        for i in range(1, self.FEELER_STEPS + 1):
            px = origin.x + feeler_dir.x * step_len * i
            py = origin.y + feeler_dir.y * step_len * i
            if self._point_in_obstacle(px, py):
                # How far along the feeler (0=tip, 1=base near dog)
                closeness = 1.0 - (i / self.FEELER_STEPS)
                # Perpendicular avoidance: rotate feeler 90° away from hit side
                if angle_deg >= 0:   # right feeler or centre → push left
                    avoid = pygame.Vector2(-feeler_dir.y, feeler_dir.x)
                else:                # left feeler → push right
                    avoid = pygame.Vector2(feeler_dir.y, -feeler_dir.x)
                return avoid * (closeness + 0.1)
        return pygame.Vector2(0, 0)

    # ------------------------------------------------------------------
    def _compute_steering(self, goal_dir):
        """
        Combine goal direction with feeler-based avoidance.
        Returns a normalised steering direction.
        """
        avoidance = pygame.Vector2(0, 0)
        for angle in self.FEELER_ANGLES:
            avoidance += self._cast_feeler(self.pos, angle, goal_dir)

        if avoidance.length() > 0:
            steering = goal_dir + avoidance * self.AVOID_WEIGHT
        else:
            steering = goal_dir

        if steering.length() > 0:
            return steering.normalize()
        return goal_dir

    # ------------------------------------------------------------------
    def _push_out_of_obstacles(self):
        """Hard push-out fallback — same as before, returns True if pushed."""
        dog_mask    = pygame.mask.from_surface(self.image)
        dog_topleft = pygame.Vector2(self.rect.topleft)
        dw = self.rect.width
        dh = self.rect.height
        pushed = False

        for obj_mask, obj_pos in collision_masks:
            offset = (int(obj_pos.x - dog_topleft.x),
                      int(obj_pos.y - dog_topleft.y))
            if not dog_mask.overlap(obj_mask, offset):
                continue

            pushes = []
            for dx in range(1, dw + 1):
                tl = (int(dog_topleft.x) + dx, int(dog_topleft.y))
                if not dog_mask.overlap(obj_mask, (int(obj_pos.x-tl[0]), int(obj_pos.y-tl[1]))):
                    pushes.append((dx, 0)); break
            for dx in range(1, dw + 1):
                tl = (int(dog_topleft.x) - dx, int(dog_topleft.y))
                if not dog_mask.overlap(obj_mask, (int(obj_pos.x-tl[0]), int(obj_pos.y-tl[1]))):
                    pushes.append((-dx, 0)); break
            for dy in range(1, dh + 1):
                tl = (int(dog_topleft.x), int(dog_topleft.y) + dy)
                if not dog_mask.overlap(obj_mask, (int(obj_pos.x-tl[0]), int(obj_pos.y-tl[1]))):
                    pushes.append((0, dy)); break
            for dy in range(1, dh + 1):
                tl = (int(dog_topleft.x), int(dog_topleft.y) - dy)
                if not dog_mask.overlap(obj_mask, (int(obj_pos.x-tl[0]), int(obj_pos.y-tl[1]))):
                    pushes.append((0, -dy)); break

            if pushes:
                best = min(pushes, key=lambda v: abs(v[0]) + abs(v[1]))
                self.rect.centerx += best[0]
                self.rect.centery += best[1]
                self.pos = pygame.Vector2(self.rect.center)
                dog_topleft = pygame.Vector2(self.rect.topleft)
                pushed = True

        return pushed

    # ------------------------------------------------------------------
    def update(self, dt):
        now = pygame.time.get_ticks()

        # Settled at bowl — idle forever
        if self._at_bowl:
            self.image = self._anims['down'][0]
            return

        # Pausing between random waypoints
        if self._pausing:
            self.image = self._anims[self._facing][0]
            if now >= self._pause_until:
                self._pausing  = False
                self._waypoint = self._pick_waypoint()
            return

        # --- Goal direction --------------------------------------------------
        to_target = self._waypoint - self.pos
        dist = to_target.length()

        if dist <= self.WAYPOINT_DIST:
            if self._fetching:
                if self._fetch_stage == 0:
                    # Reached the left-side guide point — now head to bowl
                    self._fetch_stage = 1
                    self._waypoint    = self._bowl_pos
                else:
                    # Reached the bowl — settle permanently
                    self._at_bowl  = True
                    self._fetching = False
                    self.image = self._anims['down'][0]
                    return
            else:
                self._pausing     = True
                self._pause_until = now + random.randint(self.PAUSE_MIN, self.PAUSE_MAX)
                return

        goal_dir = to_target.normalize()

        # --- Steering (feeler avoidance + goal) -----------------------------
        move_dir = self._compute_steering(goal_dir)

        self._update_facing(move_dir)
        self.pos += move_dir * self.SPEED * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Hard collision only when roaming — disabled during fetch pathfinding
        if not self._fetching:
            self._push_out_of_obstacles()

        # --- Stuck detection ------------------------------------------------
        elapsed = (now - self._last_stuck_check) / 1000.0
        if elapsed >= self.STUCK_CHECK:
            moved = (self.pos - self._pos_at_last_check).length()
            if moved < self.STUCK_DIST:
                if self._fetching:
                    # Nudge 90° sideways to unstick while keeping bowl target
                    perp = pygame.Vector2(-goal_dir.y, goal_dir.x)
                    self.pos += perp * 30
                    self.rect.center = (int(self.pos.x), int(self.pos.y))
                else:
                    self._waypoint = self._pick_waypoint()
            self._last_stuck_check  = now
            self._pos_at_last_check = pygame.Vector2(self.pos)

        self._tick_animation()

#images
background_img = pygame.image.load("images/garden.png")
player_surf = pygame.image.load("images\Player_sprites\sprite-1-1 (1).png")
house_front = pygame.image.load("images/jarrys_house.png")
#scaling the house image
house_front = pygame.transform.scale(house_front, (450, 450))
dog_house = pygame.image.load("images/dogHouse.png")
#scaling the dog house image
dog_house = pygame.transform.scale(dog_house, (150, 150))

pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

#background image scaled to fit window - sophie
background_surf = pygame.image.load("images/garden.png").convert()
background_surf = pygame.transform.scale(
    background_surf, (WINDOW_WIDTH, WINDOW_HEIGHT)
)

player_walk_forward = [pygame.image.load(f"images\Player_sprites\sprite-1-{i} (1).png") for i in range (1,5)]
player_walk_back = [pygame.image.load(f"images\Player_sprites\sprite-2-{i} (1).png") for i in range (1,5)]
player_walk_right = [pygame.image.load(f"images\Player_sprites\sprite-3-{i} (1).png") for i in range (1,5)]
player_walk_left = [pygame.image.load(f"images\Player_sprites\sprite-4-{i} (1).png") for i in range (1,5)]
player_walk_forward_right = [pygame.image.load(f"images\Player_sprites\sprite-5-{i} (1).png") for i in range (1,5)]
player_walk_forward_left = [pygame.image.load(f"images\Player_sprites\sprite-6-{i} (1).png") for i in range (1,5)]
#player_walk_back_left = [pygame.image.load(f"images\Player_sprites\sprite-1-{i} (2).png") for i in range (1,5)]
#player_walk_back_right = [pygame.image.load(f"images\Player_sprites\sprite-2-{i} (2).png") for i in range (1,5)]

#walking backwards
player_walk_back_right1 = pygame.image.load("images\Player_sprites\sprite-1-1 (2).png")
player_walk_back_left1 = pygame.image.load('images\Player_sprites\sprite-2-1 (2).png')
player_walk_back_right1 = pygame.transform.scale_by(player_walk_back_right1, 0.65)
player_walk_back_left1 = pygame.transform.scale_by(player_walk_back_left1, 0.65)
player_walk_back_right2 = pygame.image.load("images\Player_sprites\sprite-1-2 (2).png")
player_walk_back_left2 = pygame.image.load('images\Player_sprites\sprite-2-2 (2).png')
player_walk_back_right2 = pygame.transform.scale_by(player_walk_back_right2, 0.65)
player_walk_back_left2 = pygame.transform.scale_by(player_walk_back_left2, 0.65)
player_walk_back_right3 = pygame.image.load("images\Player_sprites\sprite-1-3 (2).png")
player_walk_back_left3 = pygame.image.load('images\Player_sprites\sprite-2-3 (2).png')
player_walk_back_right3 = pygame.transform.scale_by(player_walk_back_right3, 0.65)
player_walk_back_left3 = pygame.transform.scale_by(player_walk_back_left3, 0.65)
player_walk_back_right4 = pygame.image.load("images\Player_sprites\sprite-1-4 (2).png")
player_walk_back_left4 = pygame.image.load('images\Player_sprites\sprite-2-4 (2).png')
player_walk_back_right4 = pygame.transform.scale_by(player_walk_back_right4, 0.65)
player_walk_back_left4 = pygame.transform.scale_by(player_walk_back_left4, 0.65)
player_walk_back_right5 = pygame.image.load("images\Player_sprites\sprite-1-5 (2).png")
player_walk_back_left5 = pygame.image.load('images\Player_sprites\sprite-2-5 (2).png')
player_walk_back_right5 = pygame.transform.scale_by(player_walk_back_right5, 0.65)
player_walk_back_left5 = pygame.transform.scale_by(player_walk_back_left5, 0.65)

player_walk_back_right = [player_walk_back_left1,player_walk_back_left2,player_walk_back_left3,player_walk_back_left4,player_walk_back_left5]
player_walk_back_left= [player_walk_back_right1,player_walk_back_right2,player_walk_back_right3,player_walk_back_right4,player_walk_back_right5]

#dog sprite animation — 4 frames per direction
DOG_SCALE = 0.225   # 0.15 × 1.5 upscale

def _make_outline(surf, colour=(0, 0, 0, 220), thickness=2):
    """Return a new surface with a solid outline drawn around the sprite."""
    w, h = surf.get_size()
    outlined = pygame.Surface((w + thickness * 2, h + thickness * 2), pygame.SRCALPHA)
    # Stamp the sprite in each of the 8 surrounding positions using its mask
    mask = pygame.mask.from_surface(surf)
    outline_surf = mask.to_surface(setcolor=colour, unsetcolor=(0, 0, 0, 0))
    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx == 0 and dy == 0:
                continue
            outlined.blit(outline_surf, (dx + thickness, dy + thickness))
    # Draw the original sprite on top, centred
    outlined.blit(surf, (thickness, thickness))
    return outlined
dog_walk_down  = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-1-{i} (3).png").convert_alpha(), DOG_SCALE))
    for i in range(1, 5)]
dog_walk_up    = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-2-{i} (3).png").convert_alpha(), DOG_SCALE))
    for i in range(1, 5)]
dog_walk_right = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-3-{i} (2).png").convert_alpha(), DOG_SCALE))
    for i in range(1, 5)]
dog_walk_left  = [_make_outline(pygame.transform.scale_by(
    pygame.image.load(f"images/dogSprite/sprite-4-{i} (2).png").convert_alpha(), DOG_SCALE))
    for i in range(1, 5)]

# Keep single reference for the idle/starting frame (first frame of each dir)
dog_down  = dog_walk_down[0]
dog_up    = dog_walk_up[0]
dog_left  = dog_walk_left[0]
dog_right = dog_walk_right[0]

# PLAYER = Player.image
# PLAYER.set_colorkey((252, 252, 253),(0,0,95))

#Hotbar
overlay = Overlay(Player)

# ---- Inventory item definitions --------------------------------------------
shovel       = InventoryItem("Shovel",       "Tool",       "images/items/Clean_Shovel.png")
dirty_shovel = InventoryItem("Dirty_Shovel", "Tool",       "images/items/Dirty_Shovel.png")
dog_bone     = InventoryItem("Dog_Bone",     "Quest Item", "images/items/Dog_Bone.png")
mj_vinyl     = InventoryItem("MJ_Vinyl",     "Quest Item", "images/items/Vinyl_white.png")
billy_vinyl  = InventoryItem("Billy_Vinyl",  "Quest Item", "images/items/Vinyl_yellow.png")
katie_vinyl  = InventoryItem("Katie_Vinyl",  "Quest Item", "images/items/Vinyl_red.png")

overlay.hotbar.add_item(shovel, 0)   # player starts with the clean shovel

# ---- Ground items ----------------------------------------------------------
ground_items_group = pygame.sprite.Group()
ground_mj    = GroundItem(ground_items_group, mj_vinyl,    (300, 500))
ground_billy = GroundItem(ground_items_group, billy_vinyl, (750, 350))
ground_katie = GroundItem(ground_items_group, katie_vinyl, (500, 200))

# ---- Dog bowl --------------------------------------------------------------
dog_bowl = DogBowl((160, 650))

# ---- Dirt mound – lower-right quadrant ------------------------------------
dirt_mound = DirtMound((1050, 640), dog_bone, dirty_shovel)

pygame.display.set_caption('Test level')
running = True
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
player = Player(all_sprites)
dog = Dog(all_sprites, player)

# ---- Collision rects for static world objects ----------------------------
# Use pixel-mask collision derived from each image's actual opaque pixels.
# Each entry: (mask, world_topleft_pos)
def make_collision_mask(surf, dest_topleft):
    """Return (pygame.Mask, pygame.Vector2 world_topleft) for a surface."""
    return (pygame.mask.from_surface(surf), pygame.Vector2(dest_topleft))

house_mask_entry    = make_collision_mask(house_front,  (850, 5))
doghouse_mask_entry = make_collision_mask(dog_house,    (100, 500))
collision_masks = [house_mask_entry, doghouse_mask_entry]

overlay.display(display_surface)
walk_sound = pygame.mixer.Sound(join("Daniel's Room","Audios", "Grass footsteps.wav"))
walk_sound.set_volume(0.9)


while running:
    dt = clock.tick(100000)/1000


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Switch hotbar slot with 1-5
            overlay.hotbar.handle_keypress(event)

            # E key – priority: dirt mound > bowl > ground item pickup
            if event.key == pygame.K_e:
                mound_dist = pygame.Vector2(player.rect.center).distance_to(dirt_mound.pos)
                bowl_dist  = pygame.Vector2(player.rect.center).distance_to(dog_bowl.pos)

                if mound_dist <= DirtMound.INTERACT_RADIUS:
                    dirt_mound.try_dig(overlay.hotbar)
                elif bowl_dist <= DogBowl.INTERACT_RADIUS:
                    if dog_bowl.try_place_bone(overlay.hotbar):
                        dog.go_to_bowl(dog_bowl.pos)
                else:
                    # Pick up nearby ground item
                    for gitem in list(ground_items_group):
                        dist = pygame.Vector2(player.rect.center).distance_to(gitem.rect.center)
                        if dist <= GroundItem.PICKUP_RADIUS:
                            added = overlay.hotbar.add_item_first_free(gitem.inventory_item)
                            if added:
                                gitem.kill()
                            break

    # Update proximity flags
    for gitem in ground_items_group:
        dist = pygame.Vector2(player.rect.center).distance_to(gitem.rect.center)
        gitem.show_prompt = dist <= GroundItem.PICKUP_RADIUS

    bowl_dist  = pygame.Vector2(player.rect.center).distance_to(dog_bowl.pos)
    mound_dist = pygame.Vector2(player.rect.center).distance_to(dirt_mound.pos)
    dog_bowl.show_prompt   = bowl_dist  <= DogBowl.INTERACT_RADIUS
    dirt_mound.show_prompt = mound_dist <= DirtMound.INTERACT_RADIUS

    all_sprites.update(dt)
    ground_items_group.update(dt)
    dirt_mound.update(dt)

    # ---- Pixel-mask collision resolution ------------------------------------
    player_mask = pygame.mask.from_surface(player.image)
    player_topleft = pygame.Vector2(player.rect.topleft)
    pw = int(player.rect.width)
    ph = int(player.rect.height)

    for obj_mask, obj_pos in collision_masks:
        offset = (int(obj_pos.x - player_topleft.x),
                  int(obj_pos.y - player_topleft.y))
        if not player_mask.overlap(obj_mask, offset):
            continue

        pushes = []
        for dx in range(1, pw + 1):
            tl = (int(player_topleft.x) + dx, int(player_topleft.y))
            if not player_mask.overlap(obj_mask, (int(obj_pos.x - tl[0]), int(obj_pos.y - tl[1]))):
                pushes.append((dx, 0)); break
        for dx in range(1, pw + 1):
            tl = (int(player_topleft.x) - dx, int(player_topleft.y))
            if not player_mask.overlap(obj_mask, (int(obj_pos.x - tl[0]), int(obj_pos.y - tl[1]))):
                pushes.append((-dx, 0)); break
        for dy in range(1, ph + 1):
            tl = (int(player_topleft.x), int(player_topleft.y) + dy)
            if not player_mask.overlap(obj_mask, (int(obj_pos.x - tl[0]), int(obj_pos.y - tl[1]))):
                pushes.append((0, dy)); break
        for dy in range(1, ph + 1):
            tl = (int(player_topleft.x), int(player_topleft.y) - dy)
            if not player_mask.overlap(obj_mask, (int(obj_pos.x - tl[0]), int(obj_pos.y - tl[1]))):
                pushes.append((0, -dy)); break

        if pushes:
            best = min(pushes, key=lambda v: abs(v[0]) + abs(v[1]))
            player.rect.centerx += best[0]
            player.rect.centery += best[1]
            player_topleft = pygame.Vector2(player.rect.topleft)

    # draw background image
    display_surface.blit(background_surf, (0, 0))
    #draw the house
    display_surface.blit(house_front, (850, 5))
    #draw the dog house
    display_surface.blit(dog_house, (100, 500))
    player.player_walk_sound()
    all_sprites.draw(display_surface)

    # Draw ground items manually so bobbing + prompt renders correctly
    for gitem in ground_items_group:
        gitem.draw(display_surface)

    # Draw dirt mound
    dirt_mound.draw(display_surface)

    # Draw dog bowl
    dog_bowl.draw(display_surface)

    overlay.display(display_surface)

    pygame.display.update()
    
pygame.quit()


