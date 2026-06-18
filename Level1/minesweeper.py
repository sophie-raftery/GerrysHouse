
import pygame
import random
import math

# ---------------------------------------------------------------------------
# Layout constants
# ---------------------------------------------------------------------------
ROWS      = 9
COLS      = 9
NUM_MINES = 10
CELL_SIZE = 54
TOP_BAR   = 64

PANEL_W = COLS * CELL_SIZE
PANEL_H = ROWS * CELL_SIZE + TOP_BAR

# Colours
BG            = (189, 189, 189)
CELL_HIDDEN   = (160, 160, 160)
CELL_REVEALED = (210, 210, 210)
CELL_HOVER    = (180, 200, 180)
CELL_EXPLODED = (255, 80,  80)
BORDER_LIGHT  = (255, 255, 255)
BORDER_DARK   = (100, 100, 100)
MINE_COL      = (30,  30,  30)
FLAG_COL      = (220, 40,  40)

NUM_COLORS = {
    1: (0,   0,   200),
    2: (0,   130, 0),
    3: (200, 0,   0),
    4: (0,   0,   130),
    5: (130, 0,   0),
    6: (0,   130, 130),
    7: (130, 0,   130),
    8: (80,  80,  80),
}


# ---------------------------------------------------------------------------
# Board helpers
# ---------------------------------------------------------------------------
def _new_game():
    return {
        "board":     [[0] * COLS for _ in range(ROWS)],
        "revealed":  [[False] * COLS for _ in range(ROWS)],
        "flagged":   [[False] * COLS for _ in range(ROWS)],
        "first":     True,
        "over":      False,
        "won":       False,
        "exploded":  None,
        "flags":     0,
        "t_start":   None,
        "elapsed":   0,
    }


def _place_mines(board, sr, sc):
    placed = 0
    while placed < NUM_MINES:
        r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
        if board[r][c] != -1 and not (r == sr and c == sc):
            board[r][c] = -1
            placed += 1


def _fill_numbers(board):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != -1:
                board[r][c] = sum(
                    1 for dr in range(-1, 2) for dc in range(-1, 2)
                    if 0 <= r+dr < ROWS and 0 <= c+dc < COLS
                    and board[r+dr][c+dc] == -1
                )


def _reveal(board, revealed, r, c):
    if revealed[r][c]:
        return
    revealed[r][c] = True
    if board[r][c] == 0:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and not revealed[nr][nc]:
                    _reveal(board, revealed, nr, nc)


def _check_win(board, revealed):
    return all(
        revealed[r][c]
        for r in range(ROWS) for c in range(COLS)
        if board[r][c] != -1
    )


# ---------------------------------------------------------------------------
# Draw helpers
# ---------------------------------------------------------------------------
def _raised(surf, x, y, s, col):
    pygame.draw.rect(surf, col, (x, y, s, s))
    pygame.draw.line(surf, BORDER_LIGHT, (x, y+s-1), (x, y), 2)
    pygame.draw.line(surf, BORDER_LIGHT, (x, y), (x+s-1, y), 2)
    pygame.draw.line(surf, BORDER_DARK,  (x+s-1, y), (x+s-1, y+s-1), 2)
    pygame.draw.line(surf, BORDER_DARK,  (x, y+s-1), (x+s-1, y+s-1), 2)


def _sunken(surf, x, y, s, col):
    pygame.draw.rect(surf, col, (x, y, s, s))
    pygame.draw.line(surf, BORDER_DARK, (x, y+s-1), (x, y), 1)
    pygame.draw.line(surf, BORDER_DARK, (x, y), (x+s-1, y), 1)


def _mine(surf, cx, cy, r=10):
    pygame.draw.circle(surf, MINE_COL, (cx, cy), r)
    for a in range(0, 360, 45):
        ex = int(cx + (r+5)*math.cos(math.radians(a)))
        ey = int(cy + (r+5)*math.sin(math.radians(a)))
        pygame.draw.line(surf, MINE_COL, (cx, cy), (ex, ey), 2)
    pygame.draw.circle(surf, (255, 255, 255), (cx-3, cy-3), 3)


def _flag(surf, cx, cy):
    pygame.draw.line(surf, (50, 50, 50), (cx-4, cy+10), (cx-4, cy-10), 3)
    pygame.draw.polygon(surf, FLAG_COL, [(cx-4, cy-10), (cx+8, cy-4), (cx-4, cy+2)])


def _smiley(surf, cx, cy, rad, state):
    pygame.draw.circle(surf, (255, 220, 50), (cx, cy), rad)
    pygame.draw.circle(surf, (0, 0, 0), (cx, cy), rad, 2)
    if state == "win":
        for ox in (-rad+4, 2):
            pygame.draw.rect(surf, (0,0,0), (cx+ox, cy-6, rad-2, 8), border_radius=3)
        pygame.draw.line(surf, (0,0,0), (cx-5, cy-2), (cx+2, cy-2), 2)
        pygame.draw.arc(surf, (0,0,0), (cx-10, cy, 20, 14), math.pi, 0, 2)
    elif state == "dead":
        for ex, ey in [(cx-7, cy-5), (cx+3, cy-5)]:
            pygame.draw.line(surf, (0,0,0), (ex, ey), (ex+6, ey+6), 2)
            pygame.draw.line(surf, (0,0,0), (ex+6, ey), (ex, ey+6), 2)
        pygame.draw.line(surf, (0,0,0), (cx-8, cy+8), (cx+8, cy+8), 2)
    else:
        pygame.draw.circle(surf, (0,0,0), (cx-6, cy-4), 3)
        pygame.draw.circle(surf, (0,0,0), (cx+6, cy-4), 3)
        pygame.draw.arc(surf, (0,0,0), (cx-10, cy+1, 20, 12), math.pi, 0, 2)


def _overlay(surf, won):
    ov = pygame.Surface((PANEL_W, PANEL_H - TOP_BAR), pygame.SRCALPHA)
    ov.fill((0, 160, 0, 140) if won else (160, 0, 0, 140))
    surf.blit(ov, (0, TOP_BAR))
    f  = pygame.font.SysFont("Arial", 36, bold=True)
    sf = pygame.font.SysFont("Arial", 18)
    msg = "  YOU WIN!  " if won else "  GAME OVER  "
    t  = f.render(msg, True, (255, 255, 255))
    tr = t.get_rect(center=(PANEL_W//2, TOP_BAR + (PANEL_H-TOP_BAR)//2))
    surf.blit(t, tr)
    s  = sf.render("Click smiley to play again  |  ESC to exit", True, (255, 255, 255))
    surf.blit(s, s.get_rect(center=(PANEL_W//2, tr.bottom + 20)))


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run(parent_surface=None, number_images=None):
    """
    Run the minesweeper mini-game in a centred window overlay.

    Parameters
    ----------
    parent_surface : the game's display surface (used to centre the panel)
    number_images  : dict  {1: surf, 2: surf, 3: surf}  custom images for counts

    Returns True if the player won, False if they quit/lost without winning.
    """
    # Pre-scale custom images to fit inside a cell
    cell_inner = CELL_SIZE - 10
    custom = {}
    if number_images:
        for k, img in number_images.items():
            custom[k] = pygame.transform.smoothscale(img, (cell_inner, cell_inner))

    if parent_surface is None:
        parent_surface = pygame.display.get_surface()

    sw, sh = parent_surface.get_size()
    ox = (sw - PANEL_W) // 2   # panel offset x
    oy = (sh - PANEL_H) // 2   # panel offset y

    panel  = pygame.Surface((PANEL_W, PANEL_H))
    clock  = pygame.time.Clock()

    font_num   = pygame.font.SysFont("Arial", 26, bold=True)
    font_big   = pygame.font.SysFont("Consolas", 28, bold=True)
    face_rect  = pygame.Rect(PANEL_W//2 - 20, TOP_BAR//2 - 20, 40, 40)

    state = _new_game()
    hover = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_p:
                    return True   # debug: instant win

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos[0] - ox, event.pos[1] - oy
                if my > TOP_BAR:
                    r, c = (my - TOP_BAR) // CELL_SIZE, mx // CELL_SIZE
                    hover = (r, c) if 0 <= r < ROWS and 0 <= c < COLS else None
                else:
                    hover = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos[0] - ox, event.pos[1] - oy

                # Reset button
                if face_rect.collidepoint(mx, my):
                    state = _new_game()
                    continue

                if my <= TOP_BAR or state["over"] or state["won"]:
                    continue

                r, c = (my - TOP_BAR) // CELL_SIZE, mx // CELL_SIZE
                if not (0 <= r < ROWS and 0 <= c < COLS):
                    continue

                if event.button == 1:   # reveal
                    if state["flagged"][r][c] or state["revealed"][r][c]:
                        continue
                    if state["first"]:
                        _place_mines(state["board"], r, c)
                        _fill_numbers(state["board"])
                        state["first"]   = False
                        state["t_start"] = pygame.time.get_ticks()
                    _reveal(state["board"], state["revealed"], r, c)
                    if state["board"][r][c] == -1:
                        state["over"]     = True
                        state["exploded"] = (r, c)
                        for mr in range(ROWS):
                            for mc in range(COLS):
                                if state["board"][mr][mc] == -1:
                                    state["revealed"][mr][mc] = True
                    elif _check_win(state["board"], state["revealed"]):
                        state["won"] = True
                        return True    # ← signal win immediately

                elif event.button == 3:  # flag
                    if state["revealed"][r][c]:
                        continue
                    state["flagged"][r][c] = not state["flagged"][r][c]
                    state["flags"] += 1 if state["flagged"][r][c] else -1

        # Timer
        if state["t_start"] and not state["over"] and not state["won"]:
            state["elapsed"] = (pygame.time.get_ticks() - state["t_start"]) // 1000

        # --- Draw panel -----------------------------------------------------
        panel.fill(BG)

        for r in range(ROWS):
            for c in range(COLS):
                x = c * CELL_SIZE
                y = r * CELL_SIZE + TOP_BAR
                cx_cell = x + CELL_SIZE // 2
                cy_cell = y + CELL_SIZE // 2

                if state["revealed"][r][c]:
                    col = CELL_EXPLODED if (r, c) == state["exploded"] else CELL_REVEALED
                    _sunken(panel, x, y, CELL_SIZE, col)
                    val = state["board"][r][c]
                    if val == -1:
                        _mine(panel, cx_cell, cy_cell)
                    elif val > 0:
                        if val in custom:
                            panel.blit(custom[val],
                                       custom[val].get_rect(center=(cx_cell, cy_cell)))
                        else:
                            t = font_num.render(str(val), True, NUM_COLORS[val])
                            panel.blit(t, t.get_rect(center=(cx_cell, cy_cell)))
                else:
                    is_hover = (hover == (r, c)) and not state["over"]
                    _raised(panel, x, y, CELL_SIZE, CELL_HOVER if is_hover else CELL_HIDDEN)
                    if state["flagged"][r][c]:
                        _flag(panel, cx_cell, cy_cell)
                    elif (state["over"] or state["won"]) and state["board"][r][c] == -1:
                        _mine(panel, cx_cell, cy_cell)

        # Top bar
        panel.fill(BG, (0, 0, PANEL_W, TOP_BAR))
        pygame.draw.line(panel, BORDER_DARK, (0, TOP_BAR), (PANEL_W, TOP_BAR), 2)
        mines_left = NUM_MINES - state["flags"]
        ct = font_big.render(f"{max(mines_left,0):03d}", True, (200, 0, 0))
        panel.blit(ct, (10, TOP_BAR//2 - ct.get_height()//2))
        tt = font_big.render(f"{min(state['elapsed'],999):03d}", True, (200, 0, 0))
        panel.blit(tt, (PANEL_W - tt.get_width() - 10, TOP_BAR//2 - tt.get_height()//2))

        fs = "win" if state["won"] else ("dead" if state["over"] else "normal")
        _smiley(panel, face_rect.centerx, face_rect.centery, 18, fs)

        if state["over"]:
            _overlay(panel, False)
        elif state["won"]:
            _overlay(panel, True)

        # Blit panel onto parent, with a dark backdrop
        backdrop = pygame.Surface((sw, sh), pygame.SRCALPHA)
        backdrop.fill((0, 0, 0, 160))
        parent_surface.blit(backdrop, (0, 0))
        parent_surface.blit(panel, (ox, oy))
        pygame.display.update()
        clock.tick(60)
