# How to Make Gerry's House — A Complete Guide for a 16-Year-Old

---

## What Is This Game?

**Gerry's House** is a 2D top-down adventure game built in Python using a library called **pygame-ce** (a community edition of pygame). The player walks around a garden and through rooms completing tasks — finding a bone, digging it up, distracting a dog, collecting vinyl records, and eventually triggering a cutscene ending.

The whole game is made of about a dozen Python files, a folder of images, and a folder of audio files. There is no game engine like Unity or Godot — every mechanic is written by hand.

---

## What You Need Before You Start

### Software
- **Python 3.10 or newer** — download from python.org
- **pygame-ce** — install it by opening a terminal and typing:
  ```
  pip install pygame-ce
  ```
- A code editor — **VS Code** is recommended (it's free)

### File Structure
The project is organised like this:

```
GerrysHouse/
├── Level1/
│   ├── Test_level.py        ← the starting garden level
│   ├── Lvl 1 Gerry room.py  ← Gerry's bedroom (first indoor level)
│   ├── door.py              ← reusable door/transition class
│   ├── hotbar.py            ← inventory system
│   ├── shared_state.py      ← passes data between levels
│   └── minesweeper.py       ← the bed mini-game
├── Level 2/
│   ├── Lvl 2.py             ← second garden level
│   └── Kitchen Lvl 2.py     ← kitchen interior
├── Level 3/
│   ├── Lvl 3.py             ← third garden level
│   └── Garage Lvl 3.py      ← garage interior
├── Level 4/
│   ├── Lvl 4.py             ← fourth garden level
│   └── Lvl 4 Gerry room.py  ← final room with cutscene
├── Vivienne's room/
│   ├── losing_screen1.py
│   └── winning_screen1.py   (and more)
├── EndCutScene/
│   └── ending.py
└── images/                  ← all PNG sprites and backgrounds
```

---

## Core Concept — How Python Games Work

Every pygame game follows the same three-step loop, running 60 times per second:

```
1. Handle events  (keyboard, mouse, window close)
2. Update game state  (move player, check collisions, update timers)
3. Draw everything  (background, sprites, UI)
```

This is called the **game loop**. Here is the simplest possible pygame game:

```python
import pygame
pygame.init()

screen = pygame.display.set_mode((1280, 720))
clock  = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60) / 1000   # time since last frame in seconds

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))       # clear screen to black
    pygame.display.update()      # show the frame

pygame.quit()
```

Every level file in Gerry's House is basically this loop with more things added to it.

---

## Step 1 — Making the Player Move

The player is a **Sprite** — pygame's built-in class for anything that has an image and a position on screen.

```python
class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load("images/Player_sprites/sprite-1-1 (1).png").convert_alpha()
        self.rect  = self.image.get_frect(center=(640, 360))  # start in the middle
        self.direction = pygame.Vector2()
        self.speed = 150

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * self.speed * dt
```

**Key ideas:**
- `pygame.key.get_pressed()` returns which keys are held down right now
- `dt` (delta time) makes movement frame-rate independent — the player moves the same speed whether the game runs at 30fps or 120fps
- `normalize()` stops the player moving faster diagonally

In Gerry's House the player also switches between different walking animation frames depending on direction. There are 8 directions of movement, each with 4 frames of animation stored in lists:

```python
walk_forward = [image1, image2, image3, image4]  # one list per direction
```

Every 200 milliseconds, the current frame index advances by 1 and wraps back to 0.

---

## Step 2 — Collisions (Invisible Walls)

To stop the player walking through walls and furniture, the game uses **collision rectangles** — invisible boxes that push the player back out if they overlap.

```python
COLLISION_RECTS = [
    pygame.Rect(0, 0, 1280, 40),    # top wall
    pygame.Rect(0, 680, 1280, 40),  # bottom wall
    pygame.Rect(0, 0, 40, 720),     # left wall
    pygame.Rect(1240, 0, 40, 720),  # right wall
]

def resolve_collision(player):
    for wall in COLLISION_RECTS:
        if not player.rect.colliderect(wall):
            continue
        # Work out how much overlap there is in each direction
        ox = min(player.rect.right - wall.left, wall.right - player.rect.left)
        oy = min(player.rect.bottom - wall.top, wall.bottom - player.rect.top)
        # Push out by the smaller overlap
        if ox < oy:
            if player.rect.centerx < wall.centerx:
                player.rect.right = wall.left
            else:
                player.rect.left = wall.right
        else:
            if player.rect.centery < wall.centery:
                player.rect.bottom = wall.top
            else:
                player.rect.top = wall.bottom
```

Call `resolve_collision(player)` once per frame after moving the player. The player gets nudged out of any overlapping rectangles automatically.

---

## Step 3 — The Hotbar (Inventory)

The game has a 5-slot hotbar at the bottom of the screen. It is defined in `hotbar.py` and used by every level.

An **InventoryItem** is just a named object with an image:

```python
room_key = InventoryItem("Room_Key", "Key Item", "images/Key.png")
```

The **Hotbar** stores up to 5 items:

```python
hotbar.add_item_first_free(room_key)   # add to first empty slot
item = hotbar.slots[0]                 # read slot 0
hotbar.slots[0] = None                 # remove item from slot 0
```

The **Overlay** class draws the hotbar to the screen each frame:

```python
overlay = Overlay(Player)
# in the draw section of your game loop:
overlay.display(display_surface)
```

The player can press **1–5** to select a slot, and the selected slot gets a highlight border.

---

## Step 4 — Interactable Objects

Every interactable object in the game follows the same pattern:

1. Has a `pos` (position) and `rect` (hitbox)
2. Has a `show_prompt` flag that turns on when the player is close
3. Has a `draw()` method that shows a glow and `[E]` text when `show_prompt` is True
4. Logic runs when the player presses `E` and is close enough

Here is a stripped-down example — a box that gives the player a key:

```python
class KeyBox:
    INTERACT_RADIUS = 90

    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.collected = False
        self.show_prompt = False
        self.rect = pygame.Rect(0, 0, 48, 48)
        self.rect.center = (int(pos[0]), int(pos[1]))
        font = pygame.font.SysFont(None, 20)
        self._prompt = font.render("[E] Open", True, (255, 255, 255))
        self._shadow = font.render("[E] Open", True, (0, 0, 0))

    def update(self, player):
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        self.show_prompt = dist <= self.INTERACT_RADIUS and not self.collected

    def draw(self, surface):
        if self.show_prompt:
            # Draw a yellow glow circle
            glow = pygame.Surface((70, 70), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 220, 100, 70), glow.get_rect())
            surface.blit(glow, glow.get_rect(center=self.rect.center))
            # Draw the prompt text with a shadow for readability
            px = self.rect.centerx - self._prompt.get_width() // 2
            py = self.rect.top - 22
            surface.blit(self._shadow, (px + 1, py + 1))
            surface.blit(self._prompt, (px, py))

# In the game loop, on keypress E:
if event.key == pygame.K_e:
    if key_box.show_prompt:
        key_box.collected = True
        hotbar.add_item_first_free(room_key)
```

All the interactables in Gerry's House (the door, the dog bowl, the dirt mound, the bed, the vinyl box) use exactly this structure.

---

## Step 5 — The Door System (`door.py`)

Moving between levels is handled by the `Door` class. It:
- Detects when the player walks close
- Shows a `[E] Enter` prompt
- Fades the screen to black when entered
- Dynamically loads and runs the next level's Python file

```python
from door import Door

front_door = Door(
    pos           = (1004, 320),          # position on screen
    target_module = "Level1/Lvl 1 Gerry room.py",  # file to load
    image_path    = None,                 # None = invisible door
    size          = (40, 60),             # hitbox size
)

# In the update loop:
front_door.update(player)

# On keypress E:
if front_door.try_enter(player):
    front_door.transition(display_surface)   # fade to black
    front_door.load_next_level()             # run the next file

# In the draw loop:
front_door.draw(display_surface)
```

The door uses `importlib` under the hood to load any `.py` file by its path. This means you can create a new level just by making a new Python file with a `run()` function.

---

## Step 6 — Passing Inventory Between Levels (`shared_state.py`)

When the player moves from one level to another, their items need to carry over. `shared_state.py` is a tiny module with three global variables used as a data bus:

```python
# shared_state.py
incoming_hotbar_slots = None   # items going INTO the next level
returned_hotbar_slots = None   # items coming BACK from a level
player_spawn          = None   # where to place the player on return
```

When leaving a level:
```python
import shared_state
shared_state.incoming_hotbar_slots = list(overlay.hotbar.slots)
front_door.load_next_level()
```

When the next level starts:
```python
if shared_state.incoming_hotbar_slots:
    for i, item in enumerate(shared_state.incoming_hotbar_slots):
        overlay.hotbar.slots[i] = item
    shared_state.incoming_hotbar_slots = None
```

---

## Step 7 — NPC Patrol AI

The dog in Level 1, the mother in the kitchen, and the father in the garage all use the same patrol AI. It has three parts:

### 1. Patrol waypoints
A list of positions the NPC walks to in order, looping forever:

```python
PATROL = [
    pygame.Vector2(300, 110),
    pygame.Vector2(680, 100),
    pygame.Vector2(730, 450),
]
```

### 2. Steering / obstacle avoidance
Before moving, the NPC fires three "feeler" rays at -35°, 0°, and +35° ahead of it. If a ray hits a collision rectangle, the NPC steers away from it. This stops NPCs getting stuck in corners.

### 3. Stuck detection
If the NPC hasn't moved more than 4 pixels in the last 1.5 seconds, it skips to the next waypoint. This is the fallback for when the steering fails.

### Agro ring (chasing)
Each NPC also has an **agro radius** — a circle around them. When the player steps inside it, the NPC switches from patrol mode to chase mode and runs toward the player at a faster speed. If the NPC catches the player (rect overlap), the game transitions to the losing screen.

```python
player_dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
self._chasing = player_dist <= self.AGRO_RADIUS

if self._chasing:
    # Run straight at the player
    to_player = pygame.Vector2(player.rect.center) - self.pos
    move_dir  = to_player.normalize()
    self.pos += move_dir * self.CHASE_SPEED * dt
```

---

## Step 8 — Y-Sorting (Walking Behind Objects)

In a top-down game, objects closer to the bottom of the screen should appear in front of objects higher up. This is called **y-sorting**.

In the kitchen and garage, sprites are drawn in two passes around the counter/car:

```python
# Split all sprites into those above and below the counter's centre
behind  = [s for s in all_sprites if s.rect.bottom < counter_rect.centery]
infront = [s for s in all_sprites if s.rect.bottom >= counter_rect.centery]

# Draw back layer → counter → front layer
for sprite in behind:
    display_surface.blit(sprite.image, sprite.rect)
display_surface.blit(counter_img, counter_rect)
for sprite in infront:
    display_surface.blit(sprite.image, sprite.rect)
```

When the player walks above the counter's midpoint they appear behind it; below it they appear in front.

---

## Step 9 — The Level Flow (How the Game Progresses)

The game follows a linear path:

```
Test_level (garden L1)
    → Gerry's Room L1
        • Make the bed (minesweeper) → MJ_Vinyl
        • Open key box → Room_Key
        • Exit with both items
    → Back to Test_level garden
        → Lvl 2 garden
            → Kitchen L2
                • Take Billy_Vinyl from counter
                • Exit kitchen
            → Back to Lvl 2 garden
                → Lvl 3 garden
                    → Garage L3
                        • Take Katie_Vinyl from vinyl box
                        • Exit garage
                    → Back to Lvl 3 garden
                        → Lvl 4 garden
                            → Gerry's Room L4
                                • Place all 3 vinyls on the record player
                                • Watch the cutscene
                                → EndCutScene → Winning Screen
```

At each stage, the player can be caught by the dog (Level 1) or the mother/father (Levels 2 and 3), sending them to the losing screen.

---

## Step 10 — Adding a New Level (Quick-Start Template)

Copy this template to create a new level file:

```python
import pygame
import sys, os
from os.path import join

_HERE = os.path.dirname(os.path.abspath(__file__))
_LVL1 = os.path.join(_HERE, '..', 'Level1')
if _LVL1 not in sys.path:
    sys.path.insert(0, _LVL1)

from hotbar import Overlay, InventoryItem
from door   import Door
import shared_state

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(r'images\Player_sprites\sprite-1-1 (1).png').convert_alpha()
        self.rect  = self.image.get_frect(center=(640, 600))  # spawn near bottom
        self.direction = pygame.Vector2()
        self.speed = 150

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_d]) - int(keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_s]) - int(keys[pygame.K_w])
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        self.rect.center += self.direction * self.speed * dt

def run():
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("My New Level")
    clock = pygame.time.Clock()

    background = pygame.transform.scale(
        pygame.image.load("images/garden.png").convert(), (WINDOW_WIDTH, WINDOW_HEIGHT))

    exit_door = Door(
        pos           = (640, 650),
        target_module = "Level1/Test_level.py",   # where to go when exiting
        image_path    = None,
        size          = (55, 66),
    )

    overlay     = Overlay(Player)
    all_sprites = pygame.sprite.Group()
    player      = Player(all_sprites)

    # Restore hotbar from previous level
    if getattr(shared_state, 'incoming_hotbar_slots', None):
        for i, item in enumerate(shared_state.incoming_hotbar_slots):
            overlay.hotbar.slots[i] = item
        shared_state.incoming_hotbar_slots = None

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
                        shared_state.incoming_hotbar_slots = list(overlay.hotbar.slots)
                        exit_door.transition(display_surface)
                        exit_door.load_next_level()
                        return

        exit_door.update(player)
        all_sprites.update(dt)

        display_surface.blit(background, (0, 0))
        all_sprites.draw(display_surface)
        exit_door.draw(display_surface)
        overlay.display(display_surface)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    os.chdir(os.path.join(_HERE, ".."))
    run()
```

---

## Key Tips and Common Mistakes

| Problem | Fix |
|---|---|
| Player moves through walls | Make sure `resolve_collision(player)` is called every frame after `all_sprites.update(dt)` |
| Images not found | Make sure the working directory is the project root (the folder containing `images/`) |
| NPC gets stuck in a corner | Increase `FEELER_LEN` or add more waypoints away from the stuck spot |
| Animation only shows 1–2 frames | Don't reset `_frame_idx` when direction changes — let the timer drive it |
| Door loads the wrong level | Check the `target_module` path is relative to the project root, not the level folder |
| Items lost between levels | Make sure you set `shared_state.incoming_hotbar_slots` before calling `load_next_level()` |

---

## Summary of Every File

| File | Purpose |
|---|---|
| `shared_state.py` | 3-variable data bus — passes inventory and spawn info between levels |
| `hotbar.py` | `InventoryItem`, `Hotbar` (5 slots), `Overlay` HUD — used by every level |
| `door.py` | `Door` class — proximity detection, fade transition, dynamic level loading |
| `minesweeper.py` | Mini-game launched when making the bed |
| `Test_level.py` | Level 1 garden — dog, dirt mound, shovel/bone puzzle |
| `Lvl 1 Gerry room.py` | Gerry's bedroom — minesweeper bed, key box, exit needs vinyl + key |
| `Lvl 2.py` | Level 2 garden — door to kitchen, vinyl exit door |
| `Kitchen Lvl 2.py` | Kitchen — Mother NPC patrol + chase, Billy_Vinyl collectible |
| `Lvl 3.py` | Level 3 garden — garage door, vinyl exit door |
| `Garage Lvl 3.py` | Garage — Father NPC patrol + car pause + chase, Katie_Vinyl collectible |
| `Lvl 4.py` | Level 4 garden — door to final room |
| `Lvl 4 Gerry room.py` | Final room — requires all 3 vinyls, plays cutscene ending |

---

*Written for Gerry's House — a Python/pygame-ce project.*
