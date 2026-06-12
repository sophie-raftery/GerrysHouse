import pygame
import os

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

# PLAYER

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)

        self.image = pygame.image.load(
            "Donncha_room/sprites/sprite-1-1 (1).png"
        ).convert_alpha()

        self.rect = self.image.get_rect(
            center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        )

        self.direction = pygame.Vector2()
        self.speed = 300
        self.health = 3

    def update(self, dt):
        keys = pygame.key.get_pressed()

        self.direction.x = (
            int(keys[pygame.K_d]) -
            int(keys[pygame.K_a])
        )

        self.direction.y = (
            int(keys[pygame.K_s]) -
            int(keys[pygame.K_w])
        )

        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.center += self.direction * self.speed * dt

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
            os.path.join(
                "Daniel's Room",
                "Hotbar",
                "Hotbar.png"
            )
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

# SETUP

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

pygame.display.set_caption("Test Level")
clock = pygame.time.Clock()
running = True
background_img = pygame.image.load("images/garden.png")

all_sprites = pygame.sprite.Group()

player = Player(all_sprites)

overlay = Overlay(player)

# TEST ITEM

shovel = InventoryItem("Shovel","Tool","Daniel's Room/items/Clean_Shovel.png")
dirty_shovel = InventoryItem("Dirty_Shovel","Tool","Daniel's Room/items/Dirty_Shovel.png")
dog_bone = InventoryItem("Dog_Bone","Quest Item","Daniel's Room/items/Dog_Bone.png")

overlay.hotbar.add_item(shovel, 0)
overlay.hotbar.add_item(dirty_shovel, 1)
overlay.hotbar.add_item(dog_bone, 2)


while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    all_sprites.update(dt)

    display_surface.fill("lightgreen")

    display_surface.blit(
        background_img,
        (0, 0)
    )

    all_sprites.draw(display_surface)

    overlay.display(display_surface)

    pygame.display.flip()

pygame.quit()
