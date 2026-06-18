import pygame
import os

class InventoryItem:
    def __init__(self, name, item_type, img_path):
        self.name = name
        self.item_type = item_type
        self.img = pygame.image.load(img_path).convert_alpha()


class Hotbar:
    def __init__(self, player):
        self.player = player

        self.hotbar_image = pygame.image.load(
            os.path.join("Daniel's Room", "Hotbar", "Hotbar.png")
        ).convert_alpha()

        self.hotbar_rect = self.hotbar_image.get_rect(topleft=(10, 0))

        self.slots = [None] * 5
        self.selected_slot = 0  # currently highlighted slot

        # Pixel offsets of each slot centre, relative to hotbar_rect.topleft
        self.slot_positions = [
            (28,  63),
            (80,  63),
            (128, 63),
            (182, 63),
            (230, 63),
        ]

        # Font for item-name tooltip
        self.font = pygame.font.SysFont(None, 22)

    # ------------------------------------------------------------------
    def add_item(self, item, slot):
        """Place item in a specific slot."""
        if 0 <= slot < len(self.slots):
            self.slots[slot] = item

    def add_item_first_free(self, item):
        """Place item in the first empty slot. Returns True on success."""
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = item
                return True
        return False  # hotbar full

    # ------------------------------------------------------------------
    def handle_keypress(self, event):
        """Call this from the event loop to switch selected slot with 1-5."""
        slot_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
        for i, key in enumerate(slot_keys):
            if event.key == key:
                self.selected_slot = i

    # ------------------------------------------------------------------
    def draw(self, surface):
        # Draw hotbar background
        surface.blit(self.hotbar_image, self.hotbar_rect)

        for i, item in enumerate(self.slots):
            x = self.hotbar_rect.x + self.slot_positions[i][0]
            y = self.hotbar_rect.y + self.slot_positions[i][1]

            # Highlight the selected slot
            if i == self.selected_slot:
                highlight_rect = pygame.Rect(0, 0, 44, 49)
                highlight_rect.center = (x, y)
                highlight_surf = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
                highlight_surf.fill((255, 255, 100, 80))
                surface.blit(highlight_surf, highlight_rect)

            if item:
                img = pygame.transform.scale(item.img, (40, 45))
                rect = img.get_rect(center=(x, y))
                surface.blit(img, rect)

        # Draw name tooltip for the selected slot — removed


class Overlay:
    def __init__(self, player):
        self.player = player
        self.hotbar = Hotbar(player)

    def display(self, surface):
        self.hotbar.draw(surface)