import pygame#
from os.path import join

pygame.init()

WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")

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
        self.jarry_neutral = pygame.image.load(join("images/Player_Sprites/sprite_cutscene_neutral.png")).convert_alpha()

        self.jarry_sad = pygame.image.load(join("images/Player_Sprites/sprite_cutscene_sad.png")).convert_alpha()

        self.jarry_grief = pygame.image.load(join("images/Player_Sprites/sprite_cutscene_grief.png")).convert_alpha()

        self.fishbowl = pygame.image.load(join("images/fishBowl.png")).convert_alpha()

        self.patrick = pygame.image.load(join("images/patrickFish.png")).convert_alpha()

        # resize sprites
        self.jarry_neutral = pygame.transform.scale_by(self.jarry_neutral,0.5)

        self.jarry_sad = pygame.transform.scale_by(self.jarry_sad,0.5)

        self.jarry_grief = pygame.transform.scale_by(self.jarry_grief,0.5)

        self.fishbowl = pygame.transform.scale_by(self.fishbowl,1.5)

        self.patrick = pygame.transform.scale_by(self.patrick,0.5)

        #center
        self.jarry_neutral_rect = self.jarry_neutral.get_rect(center=(640, 300))

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

        # Jarry behind fish bowl
        screen.blit(jarry,(500,60))

        # fish bowl
        screen.blit(self.fishbowl,(280,60))

        # fish
        screen.blit(self.patrick,(560,230))

        # dialogue
        if self.stage < len(self.dialogue):
            text = self.font.render(self.dialogue[self.stage],True,(255,255,255))
            screen.blit(text,(420,650))

# Create cutscene
cutscene = FishCutscene()
running = True

clock = pygame.time.Clock()

# Main loop
while running:

    dt = clock.tick(60) / 1000  # seconds since last frame

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    if cutscene.active:
        cutscene.update(dt)
        cutscene.draw(screen)

    else:
        screen.fill((30, 30, 30))


    pygame.display.update()


pygame.quit()

