import pygame

class FishCutscene:

    def __init__(self):

        self.active = True
        self.timer = 0
        self.stage = 0

        # text
        self.font = pygame.font.Font(None, 45)

        self.dialogue = [
            "Patrick?",
            "Is that you??",
            "No...",
            "It can't be..."
        ]

        # load sprites
        self.jarry_neutral = pygame.image.load(
            "../images/Player_Sprites/sprite_cutscene_neutral.png"
        ).convert_alpha()

        self.jarry_sad = pygame.image.load(
            "../images/Player_Sprites/sprite_cutscene_sad.png"
        ).convert_alpha()

        self.jarry_grief = pygame.image.load(
            "../images/Player_Sprites/sprite_cutscene_grief.png"
        ).convert_alpha()

        self.fishbowl = pygame.image.load(
            "..images/fishBowl.png"
        ).convert_alpha()

        self.patrick = pygame.image.load(
            "..images/patrickFish.png"
        ).convert_alpha()

        # resize sprites
        self.jarry_neutral = pygame.transform.scale_by(
            self.jarry_neutral,
            0.8
        )

        self.jarry_sad = pygame.transform.scale_by(
            self.jarry_sad,
            0.8
        )

        self.jarry_grief = pygame.transform.scale_by(
            self.jarry_grief,
            0.8
        )

        self.fishbowl = pygame.transform.scale_by(
            self.fishbowl,
            0.5
        )

        self.patrick = pygame.transform.scale_by(
            self.patrick,
            0.5
        )

    def update(self, dt):
        self.timer += dt

        # change scene every 3 seconds
        if self.timer >= 3:
            self.timer = 0
            self.stage += 1

        # finish cutscene
        if self.stage >= len(self.dialogue):
            self.active = False

    def draw(self, screen):
        # black background
        screen.fill((0,0,0))

        # choose Jarry emotion
        if self.stage == 0:
            jarry = self.jarry_neutral

        elif self.stage < 3:
            jarry = self.jarry_sad

        else:
            jarry = self.jarry_grief

        # Jarry behind bowl
        screen.blit(
            jarry,
            (
                450,
                80
            )
        )

        # fish bowl
        screen.blit(
            self.fishbowl,
            (
                520,
                320
            )
        )

        # fish
        screen.blit(
            self.patrick,
            (
                560,
                340
            )
        )

        # dialogue
        if self.stage < len(self.dialogue):
            text = self.font.render(
                self.dialogue[self.stage],
                True,
                (255,255,255)
            )
            screen.blit(
                text,
                (
                    420,
                    650
                )
            )