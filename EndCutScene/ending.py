import pygame
import subprocess
import sys
from os.path import join, abspath, dirname
 
pygame.init()
WINDOW_SIZE = (1280, 720)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Jarry's House")
 
 
# ── Spotlight helper ──────────────────────────────────────────────────────────
def make_spotlight(screen_w, screen_h, cx, cy, radius, darkness=210, extras=None):
    """Dark overlay with soft transparent circles punched through it.
    extras: list of (cx, cy, radius) tuples for additional lights.
    """
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, darkness))
    steps = 60
 
    def _punch(ox, oy, r):
        for i in range(steps, 0, -1):
            t     = i / steps
            alpha = int(darkness * (t ** 1.8))
            sr    = int(r * (1 - t / steps))
            pygame.draw.circle(overlay, (0, 0, 0, alpha), (ox, oy), r - sr)
        pygame.draw.circle(overlay, (0, 0, 0, 0), (ox, oy), int(r * 0.45))
 
    _punch(cx, cy, radius)
    if extras:
        for ex, ey, er in extras:
            _punch(ex, ey, er)
 
    return overlay
 
 
# ── States ────────────────────────────────────────────────────────────────────
CUTSCENE  = 0
ZOOM_OUT  = 1   # parents revealed, 5-second hold
GAME_OVER = 2
 
 
class FishCutscene:
    def __init__(self):
        self.state = CUTSCENE
        self.time  = 0
        self.stage = 0
 
        # ── Fonts ─────────────────────────────────────────────────────────────
        self.font    = pygame.font.Font(None, 52)
        self.dialogue = [
            "Patrick?",
            "Is that you??",
            "No...",
            "It can't be...",
        ]
 
        # ── Load ──────────────────────────────────────────────────────────────
        self.jarry_neutral = pygame.image.load(
            join("images", "Player_sprites", "sprite_cutscene_neutral.png")).convert_alpha()
        self.jarry_sad = pygame.image.load(
            join("images", "Player_sprites", "sprite_cutscene_sad.png")).convert_alpha()
        self.jarry_grief = pygame.image.load(
            join("images", "Player_sprites", "sprite_cutscene_grief.png")).convert_alpha()
        self.fishbowl = pygame.image.load(join("images", "patrickInFishBowlTransparent (1).png")).convert_alpha()
        self.stairs   = pygame.image.load(
            join("images", "stairs_final_scene.png")).convert_alpha()
        self.dad    = pygame.image.load(
            join("images", "Dad_sprites",    "sprite-1-1.png")).convert_alpha()
        self.mother = pygame.image.load(
            join("images", "mother_sprites", "sprite-1-1.png")).convert_alpha()
        self.game_over_img = pygame.image.load(
            join("images", "game_over.png")).convert_alpha()
        self.retry_btn = pygame.image.load(
            join("images", "buttons", "restart_button.png")).convert_alpha()
        self.exit_btn  = pygame.image.load(
            join("images", "buttons", "exit button.png")).convert_alpha()
 
        # ── Scale ─────────────────────────────────────────────────────────────
        self.jarry_neutral = pygame.transform.scale_by(self.jarry_neutral, 0.5)
        self.jarry_sad     = pygame.transform.scale_by(self.jarry_sad,     0.5)
        self.jarry_grief   = pygame.transform.scale_by(self.jarry_grief,   0.5)
        self.fishbowl      = pygame.transform.scale_by(self.fishbowl,      1.3)
 
        sw, sh = self.stairs.get_size()
        self.stairs = pygame.transform.scale(self.stairs, (420, int(sh * 420 / sw)))
 
        self.dad    = pygame.transform.scale_by(self.dad,    2.8875)
        self.mother = pygame.transform.scale_by(self.mother, 2.8875)
 
        go_w = int(WINDOW_SIZE[0] * 0.6)
        gw, gh = self.game_over_img.get_size()
        self.game_over_img = pygame.transform.scale(
            self.game_over_img, (go_w, int(gh * go_w / gw)))
 
        # ── Close-up positions ────────────────────────────────────────────────
        jarry_w, jarry_h = self.jarry_neutral.get_size()
        bowl_w,  bowl_h  = self.fishbowl.get_size()
 
        self.jarry_x = 680
        self.jarry_y = 80
        self.bowl_x  = 180
        self.bowl_y  = 150
 
        # Spotlight on Jarry's face
        self.spot_cx = self.jarry_x + jarry_w // 2
        self.spot_cy = self.jarry_y + int(jarry_h * 0.35) - 70
        self.spot_r  = 230
        # Spotlight on Jarry's face + bowl
        bowl_cx_spot = self.bowl_x + bowl_w // 2
        bowl_cy_spot = self.bowl_y + bowl_h // 2
        self._spotlight = make_spotlight(
            WINDOW_SIZE[0], WINDOW_SIZE[1],
            self.spot_cx, self.spot_cy, self.spot_r, darkness=200,
            extras=[(bowl_cx_spot, bowl_cy_spot, int(bowl_w * 0.7))])
 
        # ── Zoom-out layout (60% scale) ───────────────────────────────────────
        ZS = 0.60
 
        def _zoom(surf):
            w, h = surf.get_size()
            return pygame.transform.scale(surf, (int(w * ZS), int(h * ZS)))
 
        self.z_jarry_neutral = _zoom(self.jarry_neutral)
        self.z_jarry_sad     = _zoom(self.jarry_sad)
        self.z_jarry_grief   = _zoom(self.jarry_grief)
        self.z_bowl          = _zoom(self.fishbowl)
        self.z_stairs        = _zoom(self.stairs)
        self.z_dad           = _zoom(self.dad)
        self.z_mother        = _zoom(self.mother)
 
        zjarry_w, zjarry_h = self.z_jarry_neutral.get_size()
        zbowl_w,  zbowl_h  = self.z_bowl.get_size()
        zstair_w, zstair_h = self.z_stairs.get_size()
        zdad_w,   zdad_h   = self.z_dad.get_size()
        zmom_w,   zmom_h   = self.z_mother.get_size()
 
        self.z_jarry_x = WINDOW_SIZE[0] // 2 - zjarry_w // 2
        self.z_jarry_y = WINDOW_SIZE[1] - zjarry_h - 20
 
        self.z_bowl_x = 30
        self.z_bowl_y = WINDOW_SIZE[1] - zbowl_h - 20
 
        self.z_stair_x = WINDOW_SIZE[0] - zstair_w - 10
        self.z_stair_y = WINDOW_SIZE[1] - zstair_h - 10
 
        self.z_dad_x = self.z_stair_x + zstair_w // 2 - zdad_w // 2 + 15
        self.z_dad_y = self.z_stair_y + int(zstair_h * 0.10) - zdad_h
 
        self.z_mom_x = self.z_stair_x + zstair_w // 2 - zmom_w // 2 - 10
        self.z_mom_y = self.z_stair_y + int(zstair_h * 0.38) - zmom_h
 
        self.z_spot_cx = self.z_jarry_x + zjarry_w // 2
        self.z_spot_cy = self.z_jarry_y + int(zjarry_h * 0.20) - 7
        # Bowl spotlight centre
        z_bowl_cx = self.z_bowl_x + zbowl_w // 2
        z_bowl_cy = self.z_bowl_y + zbowl_h // 2
        # Parents spotlight — centred between dad and mother
        parents_cx = (self.z_dad_x + zdad_w // 2 + self.z_mom_x + zmom_w // 2) // 2
        parents_cy = (self.z_dad_y + self.z_mom_y + zmom_h) // 2
        parents_r  = int(max(zdad_w, zmom_w) * 2.0)   # wide enough to cover both
        # Text spotlight — bottom centre of screen where dialogue sits
        text_cx = WINDOW_SIZE[0] // 2
        text_cy = 648
        text_r  = 220
        # Speech bubble spotlight — above dad's head where bubble tip is
        zdad_w_tmp, _ = self.z_dad.get_size()
        bubble_tip_x  = self.z_dad_x + zdad_w_tmp // 2
        bubble_tip_y  = self.z_dad_y + 10
        bubble_spot_r = 160
        self._z_spotlight = make_spotlight(
            WINDOW_SIZE[0], WINDOW_SIZE[1],
            self.z_spot_cx, self.z_spot_cy, int(self.spot_r * ZS * 1.4),
            darkness=190,
            extras=[
                (z_bowl_cx,     z_bowl_cy,     int(zbowl_w * 0.7)),
                (parents_cx,    parents_cy,    parents_r),
                (text_cx,       text_cy,       text_r),
                (bubble_tip_x,  bubble_tip_y,  bubble_spot_r),
            ])
 
        # ── Game-over button positions ────────────────────────────────────────
        cx = WINDOW_SIZE[0] // 2
        self.go_img_rect = self.game_over_img.get_rect(center=(cx, 280))
        self.retry_btn  = pygame.transform.scale(self.retry_btn, (350, 300))   # scale first
        self.retry_rect = self.retry_btn.get_rect(center=(cx, 550)) 
        self.exit_rect   = self.exit_btn.get_rect(center=(cx, 640))
 
    # ── Helpers ───────────────────────────────────────────────────────────────
    def _launch_main_menu(self):
        import sys, os, importlib.util
        root_dir = abspath(join(dirname(abspath(__file__)), ".."))
        lvl1     = join(root_dir, "Level1")
        if lvl1 not in sys.path:
            sys.path.insert(0, lvl1)
        import shared_state
        pygame.mixer.music.stop()

        restart = getattr(shared_state, 'restart_level', None)
        if restart:
            shared_state.restart_level = None
            level_path = join(root_dir, restart)
            spec   = importlib.util.spec_from_file_location("_restart_lvl", level_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "run"):
                module.run()
        else:
            menu_path = join(root_dir, "Vivienne's room", "home_screen.py")
            subprocess.Popen([sys.executable, menu_path], cwd=root_dir)
 
    def _current_jarry(self, zoomed=False):
        if zoomed:
            if self.stage == 0:  return self.z_jarry_neutral
            elif self.stage < 3: return self.z_jarry_sad
            else:                return self.z_jarry_grief
        else:
            if self.stage == 0:  return self.jarry_neutral
            elif self.stage < 3: return self.jarry_sad
            else:                return self.jarry_grief
 
    def _draw_speech_bubble(self, surface, text, tip_x, tip_y):
        bubble_font = pygame.font.Font(None, 28)
        padding     = 14
        txt_surf    = bubble_font.render(text, True, (0, 0, 0))
        tw, th      = txt_surf.get_size()
        bw, bh      = tw + padding * 2, th + padding * 2
        tail_h      = 18
        # Anchor box so it ends at tip_x (expands to the left)
        bx = tip_x - bw
        by = tip_y - bh - tail_h - 4
        bubble_rect = pygame.Rect(bx, by, bw, bh)
        pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=10)
        pygame.draw.rect(surface, (30, 30, 30),   bubble_rect, width=2, border_radius=10)
        tail_pts = [(tip_x - 8, by + bh), (tip_x + 8, by + bh), (tip_x, tip_y)]
        pygame.draw.polygon(surface, (255, 255, 255), tail_pts)
        pygame.draw.lines(surface, (30, 30, 30), False,
                          [(tip_x - 8, by + bh), (tip_x, tip_y), (tip_x + 8, by + bh)], 2)
        surface.blit(txt_surf, (bx + padding, by + padding))
 
    def _advance_cutscene(self):
        self.time  = 0
        self.stage += 1
        if self.stage >= len(self.dialogue):
            self.state = ZOOM_OUT
            self.time  = 0
            pygame.mixer.music.load(join("Daniel's Room", "Audios", "loseaudio.mp3"))
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1)
 
    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt):
        self.time += dt
        if self.state == CUTSCENE:
            if self.time >= 3:
                self._advance_cutscene()
        elif self.state == ZOOM_OUT:
            if self.time >= 5:
                self.state = GAME_OVER
                self.time  = 0
 
    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface):
        if self.state == CUTSCENE:
            surface.fill((0, 0, 0))
            surface.blit(self._current_jarry(), (self.jarry_x, self.jarry_y))
            surface.blit(self.fishbowl,         (self.bowl_x,  self.bowl_y))
            surface.blit(self._spotlight, (0, 0))
            if self.stage < len(self.dialogue):
                line   = self.dialogue[self.stage]
                shadow = self.font.render(line, True, (0, 0, 0))
                text   = self.font.render(line, True, (255, 255, 255))
                tx = WINDOW_SIZE[0] // 2 - text.get_width() // 2
                surface.blit(shadow, (tx + 2, 642))
                surface.blit(text,   (tx,     640))
 
        elif self.state == ZOOM_OUT:
            surface.fill((0, 0, 0))
            jarry = self._current_jarry(zoomed=True)
            surface.blit(self.z_stairs, (self.z_stair_x, self.z_stair_y))
            surface.blit(self.z_dad,    (self.z_dad_x,   self.z_dad_y))
            surface.blit(self.z_mother, (self.z_mom_x,   self.z_mom_y))
            zdad_w, _ = self.z_dad.get_size()
            self._draw_speech_bubble(surface,
                                     "Well, what are you doing here",
                                     self.z_dad_x + zdad_w // 2,
                                     self.z_dad_y + 10)
            surface.blit(jarry,       (self.z_jarry_x, self.z_jarry_y))
            surface.blit(self.z_bowl, (self.z_bowl_x,  self.z_bowl_y))
            surface.blit(self._z_spotlight, (0, 0))
            line   = self.dialogue[-1]
            shadow = self.font.render(line, True, (0, 0, 0))
            text   = self.font.render(line, True, (255, 255, 255))
            tx = WINDOW_SIZE[0] // 2 - text.get_width() // 2
            surface.blit(shadow, (tx + 2, 642))
            surface.blit(text,   (tx,     640))
 
        elif self.state == GAME_OVER:
            surface.fill((20, 20, 20))
            surface.blit(self.game_over_img, self.go_img_rect)
            surface.blit(self.retry_btn,     self.retry_rect)
            surface.blit(self.exit_btn,      self.exit_rect)
 
    def handle_click(self, pos):
        if self.state != GAME_OVER:
            return False
        if self.retry_rect.collidepoint(pos):
            self._launch_main_menu()
            return True
        if self.exit_rect.collidepoint(pos):
            pygame.mixer.music.stop()
            return True
        return False
 
 
# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    """Entry point — stops any playing music, runs the cutscene, then returns."""
    pygame.mixer.music.stop()   # silence whatever level music was playing

    cutscene = FishCutscene()
    clock    = pygame.time.Clock()
    running  = True

    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if cutscene.state == GAME_OVER:
                    if cutscene.handle_click(event.pos):
                        running = False
                elif cutscene.state == CUTSCENE:
                    cutscene._advance_cutscene()

            if event.type == pygame.KEYDOWN:
                if cutscene.state == CUTSCENE:
                    cutscene._advance_cutscene()

        cutscene.update(dt)
        cutscene.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    run()
    pygame.quit()
