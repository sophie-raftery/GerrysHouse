"""
door.py – Reusable interactable door / level-transition object.

Usage in any level file:
    from door import Door

    # Create a door at world position (x, y) that leads to "Level2/level2.py"
    front_door = Door(
        pos          = (920, 390),          # world position (centerx, centery)
        target_module= "Level2.level2",     # importlib path to the next level
        image_path   = "images/door.png",   # optional custom sprite (None = coloured rect)
        size         = (40, 60),            # drawn size in pixels
    )

    # In your event loop (KEYDOWN E):
    if front_door.try_enter(player):
        front_door.transition(display_surface)   # fade out
        front_door.load_next_level()             # hand off to next module

    # In your update loop:
    front_door.update(player)        # sets show_prompt each frame

    # In your draw loop (after background, before HUD):
    front_door.draw(display_surface)
"""

import pygame
import importlib


class Door:
    """
    A world-space door that the player can walk up to and press E to enter.

    Parameters
    ----------
    pos           : (x, y) centre of the door in world space
    target_module : dotted import path of the next level  e.g. "Level2.level2"
    image_path    : path to a door sprite PNG, or None for a coloured placeholder
    size          : (width, height) to scale the sprite/placeholder to
    interact_radius: how close the player must be to see the prompt (px)
    fade_speed    : alpha added per frame during the transition fade (0-255)
    """

    INTERACT_RADIUS = 80

    def __init__(self, pos, target_module, image_path=None,
                 size=(40, 60), interact_radius=80, fade_speed=6):

        self.pos           = pygame.Vector2(pos)
        self.target_module = target_module
        self.interact_radius = interact_radius
        self.fade_speed    = fade_speed

        # ---- Sprite ---------------------------------------------------------
        if image_path:
            raw = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(raw, size)
        else:
            # Placeholder: a warm amber rectangle so you can see it in the world
            self.image = pygame.Surface(size, pygame.SRCALPHA)
            self.image.fill((200, 140, 60, 220))
            pygame.draw.rect(self.image, (120, 70, 20), self.image.get_rect(), 3)

        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # ---- Prompt text ----------------------------------------------------
        font = pygame.font.SysFont(None, 20)
        self._prompt_surf   = font.render("[E] Enter", True, (255, 255, 255))
        self._prompt_shadow = font.render("[E] Enter", True, (0, 0, 0))

        self.show_prompt = False   # set each frame by update()

    # ------------------------------------------------------------------
    def update(self, player):
        """Call once per frame to refresh the proximity prompt."""
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        self.show_prompt = dist <= self.interact_radius

    # ------------------------------------------------------------------
    def try_enter(self, player):
        """
        Returns True if the player is close enough to trigger the door.
        Call this from your KEYDOWN E handler.
        """
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        return dist <= self.interact_radius

    # ------------------------------------------------------------------
    def transition(self, surface):
        """
        Plays a full-screen black fade-out before switching levels.
        Blocks until the fade completes (~0.7 s at default speed).
        """
        clock   = pygame.time.Clock()
        overlay = pygame.Surface(surface.get_size())
        overlay.fill((0, 0, 0))

        for alpha in range(0, 256, self.fade_speed):
            overlay.set_alpha(alpha)
            surface.blit(overlay, (0, 0))
            pygame.display.update()
            clock.tick(60)

    # ------------------------------------------------------------------
    def load_next_level(self):
        """
        Dynamically imports and runs the target level module.
        Supports dotted module names OR absolute file paths (for filenames with spaces).
        """
        import importlib.util, os
        # If target_module looks like a file path, load it directly
        if os.path.isfile(self.target_module):
            spec   = importlib.util.spec_from_file_location("_next_level", self.target_module)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            module = importlib.import_module(self.target_module)
        if hasattr(module, "run"):
            module.run()

    # ------------------------------------------------------------------
    def draw(self, surface):
        """Draw the door sprite and the interaction prompt when close."""
        # Subtle glow when player is nearby
        if self.show_prompt:
            glow = pygame.Surface((self.rect.width + 30, self.rect.height + 30),
                                  pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (255, 220, 100, 60), glow.get_rect())
            surface.blit(glow, glow.get_rect(center=self.rect.center))

        surface.blit(self.image, self.rect)

        if self.show_prompt:
            px = self.rect.centerx - self._prompt_surf.get_width() // 2
            py = self.rect.top - 22
            surface.blit(self._prompt_shadow, (px + 1, py + 1))
            surface.blit(self._prompt_surf,   (px,     py))
