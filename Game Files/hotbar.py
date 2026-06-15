import pygame
import os
# INVENTORY ITEM

class InventoryItem:
    def __init__(self, name, item_type, img_path):
        self.name = name
        self.item_type = item_type

        self.img = pygame.image.load(
            img_path
        ).convert_alpha()

# HOTBAR

class Hotbar:
    def __init__(self, player):
        self.player = player

        self.hotbar_image = pygame.image.load(
            os.path.join("Daniel's Room","Hotbar", "Hotbar.png" )
        ).convert_alpha()

        self.hotbar_rect = self.hotbar_image.get_rect(
            topleft=(10, 0)
        )

        self.slots = [None] * 5

        # Change these values if you want
        # the items to move.
        self.slot_positions = [
            (28, 63),
            (80, 63),
            (128, 63),
            (182, 63),
            (230, 63)
        ]

    def add_item(self, item, slot):
        if 0 <= slot < len(self.slots):
            self.slots[slot] = item

    def draw(self, surface):
        # Draw hotbar first
        surface.blit(
            self.hotbar_image,
            self.hotbar_rect
        )

        # Draw items on top
        for i, item in enumerate(self.slots):
            if item:

                img = pygame.transform.scale(
                    item.img,
                    (40, 45)
                )

                x = (
                    self.hotbar_rect.x +
                    self.slot_positions[i][0]
                )

                y = (
                    self.hotbar_rect.y +
                    self.slot_positions[i][1]
                )

                rect = img.get_rect(
                    center=(x, y)
                )

                surface.blit(img, rect)

                # Debug marker
                # pygame.draw.circle(
                #     surface,
                #     "red",
                #     (x, y),
                #     3
                # )

# OVERLAY
class Overlay:
    def __init__(self, player):
        self.player = player
        self.hotbar = Hotbar(player)

    def display(self, surface):
        self.hotbar.draw(surface)

