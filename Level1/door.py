
import pygame
import importlib


class Door:

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
            # Invisible — no appearance at distance, glow+prompt shown when nearby
            self.image = pygame.Surface(size, pygame.SRCALPHA)

        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # ---- Prompt text ----------------------------------------------------
        font = pygame.font.SysFont(None, 20)
        self._prompt_surf   = font.render("[E] Enter", True, (255, 255, 255))
        self._prompt_shadow = font.render("[E] Enter", True, (0, 0, 0))

        self.show_prompt = False   # set each frame by update()

    # ------------------------------------------------------------------
    def update(self, player):
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        self.show_prompt = dist <= self.interact_radius

    # ------------------------------------------------------------------
    def try_enter(self, player):
        dist = pygame.Vector2(player.rect.center).distance_to(self.pos)
        return dist <= self.interact_radius

    # ------------------------------------------------------------------
    def transition(self, surface):
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
