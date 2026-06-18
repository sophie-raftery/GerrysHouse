import pygame
import random
import sys

# --- Settings ---
ROWS = 9
COLS = 9
NUM_MINES = 10
CELL_SIZE = 50
MARGIN = 2

# Top bar height (for status + timer)
TOP_BAR = 60
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + TOP_BAR

# Colours
BG_COLOR         = (189, 189, 189)
CELL_HIDDEN      = (160, 160, 160)
CELL_REVEALED    = (210, 210, 210)
CELL_HOVER       = (180, 180, 180)
BORDER_DARK      = (100, 100, 100)
BORDER_LIGHT     = (255, 255, 255)
MINE_COLOR       = (30, 30, 30)
FLAG_COLOR       = (220, 40, 40)
FLAGPOLE_COLOR   = (50, 50, 50)
EXPLODED_COLOR   = (255, 80, 80)
TEXT_COLOR       = (20, 20, 20)
WIN_OVERLAY      = (0, 180, 0, 160)
LOSE_OVERLAY     = (180, 0, 0, 160)

# Number colours (classic minesweeper palette)
NUM_COLORS = {
    1: (0, 0, 200),
    2: (0, 130, 0),
    3: (200, 0, 0),
    4: (0, 0, 130),
    5: (130, 0, 0),
    6: (0, 130, 130),
    7: (130, 0, 130),
    8: (80, 80, 80),
}

# --- Board logic ---

def create_board():
    return [[0] * COLS for _ in range(ROWS)]

def place_mines(board, safe_r, safe_c):
    placed = 0
    while placed < NUM_MINES:
        r = random.randint(0, ROWS - 1)
        c = random.randint(0, COLS - 1)
        if board[r][c] != -1 and not (r == safe_r and c == safe_c):
            board[r][c] = -1
            placed += 1

def fill_numbers(board):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != -1:
                count = 0
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == -1:
                            count += 1
                board[r][c] = count

def reveal(board, revealed, r, c):
    if revealed[r][c]:
        return
    revealed[r][c] = True
    if board[r][c] == 0:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and not revealed[nr][nc]:
                    reveal(board, revealed, nr, nc)

def check_win(board, revealed):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != -1 and not revealed[r][c]:
                return False
    return True

# --- Drawing helpers ---

def draw_raised_cell(surface, x, y, size, color):
    """Draws a cell with a classic raised 3D border."""
    pygame.draw.rect(surface, color, (x, y, size, size))
    # Light top/left edges
    pygame.draw.line(surface, BORDER_LIGHT, (x, y + size - 1), (x, y), 2)
    pygame.draw.line(surface, BORDER_LIGHT, (x, y), (x + size - 1, y), 2)
    # Dark bottom/right edges
    pygame.draw.line(surface, BORDER_DARK, (x + size - 1, y), (x + size - 1, y + size - 1), 2)
    pygame.draw.line(surface, BORDER_DARK, (x, y + size - 1), (x + size - 1, y + size - 1), 2)

def draw_sunken_cell(surface, x, y, size, color):
    """Draws a flat revealed cell with a subtle sunken border."""
    pygame.draw.rect(surface, color, (x, y, size, size))
    pygame.draw.line(surface, BORDER_DARK, (x, y + size - 1), (x, y), 1)
    pygame.draw.line(surface, BORDER_DARK, (x, y), (x + size - 1, y), 1)

def draw_mine(surface, cx, cy, radius=10):
    pygame.draw.circle(surface, MINE_COLOR, (cx, cy), radius)
    # Spikes
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        ex = int(cx + (radius + 5) * math.cos(rad))
        ey = int(cy + (radius + 5) * math.sin(rad))
        pygame.draw.line(surface, MINE_COLOR, (cx, cy), (ex, ey), 2)
    # Shine dot
    pygame.draw.circle(surface, (255, 255, 255), (cx - 3, cy - 3), 3)

def draw_flag(surface, cx, cy):
    pole_x = cx - 4
    pygame.draw.line(surface, FLAGPOLE_COLOR, (pole_x, cy + 10), (pole_x, cy - 10), 3)
    flag_points = [(pole_x, cy - 10), (pole_x + 12, cy - 4), (pole_x, cy + 2)]
    pygame.draw.polygon(surface, FLAG_COLOR, flag_points)

def draw_smiley(surface, cx, cy, radius, state):
    """Draw a smiley/dead/cool face button in the top bar."""
    # Face
    face_color = (255, 220, 50)
    pygame.draw.circle(surface, face_color, (cx, cy), radius)
    pygame.draw.circle(surface, (0, 0, 0), (cx, cy), radius, 2)

    if state == "win":
        # Sunglasses
        pygame.draw.rect(surface, (0, 0, 0), (cx - radius + 4, cy - 6, radius - 2, 8), border_radius=3)
        pygame.draw.rect(surface, (0, 0, 0), (cx + 2, cy - 6, radius - 2, 8), border_radius=3)
        pygame.draw.line(surface, (0, 0, 0), (cx - 5, cy - 2), (cx + 2, cy - 2), 2)
        # Smile
        pygame.draw.arc(surface, (0, 0, 0),
                        (cx - 10, cy, 20, 14), 3.14, 0, 2)
    elif state == "dead":
        # X eyes
        for ex, ey in [(cx - 7, cy - 5), (cx + 3, cy - 5)]:
            pygame.draw.line(surface, (0, 0, 0), (ex, ey), (ex + 6, ey + 6), 2)
            pygame.draw.line(surface, (0, 0, 0), (ex + 6, ey), (ex, ey + 6), 2)
        # Flat mouth
        pygame.draw.line(surface, (0, 0, 0), (cx - 8, cy + 8), (cx + 8, cy + 8), 2)
    else:
        # Normal eyes
        pygame.draw.circle(surface, (0, 0, 0), (cx - 6, cy - 4), 3)
        pygame.draw.circle(surface, (0, 0, 0), (cx + 6, cy - 4), 3)
        # Smile
        pygame.draw.arc(surface, (0, 0, 0),
                        (cx - 10, cy + 1, 20, 12), 3.14, 0, 2)

def draw_board(surface, board, revealed, flagged, hover, game_over, exploded, font):
    surface.fill(BG_COLOR)

    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE + TOP_BAR

            is_hover = (hover == (r, c)) and not revealed[r][c] and not game_over

            if revealed[r][c]:
                cell_color = EXPLODED_COLOR if (r, c) == exploded else CELL_REVEALED
                draw_sunken_cell(surface, x, y, CELL_SIZE, cell_color)

                if board[r][c] == -1:
                    draw_mine(surface, x + CELL_SIZE // 2, y + CELL_SIZE // 2)
                elif board[r][c] > 0:
                    num_surf = font.render(str(board[r][c]), True, NUM_COLORS[board[r][c]])
                    nr = num_surf.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                    surface.blit(num_surf, nr)
            else:
                cell_color = CELL_HOVER if is_hover else CELL_HIDDEN
                draw_raised_cell(surface, x, y, CELL_SIZE, cell_color)

                if flagged[r][c]:
                    draw_flag(surface, x + CELL_SIZE // 2, y + CELL_SIZE // 2)
                elif game_over and board[r][c] == -1:
                    # Reveal all mines on game over
                    draw_mine(surface, x + CELL_SIZE // 2, y + CELL_SIZE // 2)

def draw_top_bar(surface, mines_left, elapsed, face_state, face_rect, font_big, font_small):
    pygame.draw.rect(surface, BG_COLOR, (0, 0, WIDTH, TOP_BAR))
    pygame.draw.line(surface, BORDER_DARK, (0, TOP_BAR), (WIDTH, TOP_BAR), 2)

    # Mine counter (left)
    mine_text = font_big.render(f"{max(mines_left, 0):03d}", True, (200, 0, 0))
    surface.blit(mine_text, (10, TOP_BAR // 2 - mine_text.get_height() // 2))

    # Timer (right)
    timer_text = font_big.render(f"{min(elapsed, 999):03d}", True, (200, 0, 0))
    surface.blit(timer_text, (WIDTH - timer_text.get_width() - 10,
                               TOP_BAR // 2 - timer_text.get_height() // 2))

    # Smiley face button (center)
    draw_smiley(surface, face_rect.centerx, face_rect.centery, 18, face_state)

    # Hint text
    hint = font_small.render("Left click: reveal   Right click: flag", True, TEXT_COLOR)
    # (skipped to keep bar clean — shown in window title instead)

def draw_overlay(surface, message):
    overlay = pygame.Surface((WIDTH, HEIGHT - TOP_BAR), pygame.SRCALPHA)
    color = (0, 160, 0, 140) if "WIN" in message else (160, 0, 0, 140)
    overlay.fill(color)
    surface.blit(overlay, (0, TOP_BAR))

    font = pygame.font.SysFont("Arial", 36, bold=True)
    text = font.render(message, True, (255, 255, 255))
    tr = text.get_rect(center=(WIDTH // 2, TOP_BAR + (HEIGHT - TOP_BAR) // 2))
    surface.blit(text, tr)

    sub_font = pygame.font.SysFont("Arial", 18)
    sub = sub_font.render("Click the smiley to play again", True, (255, 255, 255))
    sr = sub.get_rect(center=(WIDTH // 2, tr.bottom + 20))
    surface.blit(sub, sr)

# --- Main game loop ---

def new_game():
    return {
        "board":    create_board(),
        "revealed": [[False] * COLS for _ in range(ROWS)],
        "flagged":  [[False] * COLS for _ in range(ROWS)],
        "first_move": True,
        "game_over":  False,
        "won":        False,
        "exploded":   None,
        "flags_placed": 0,
        "start_ticks":  None,
        "elapsed":      0,
    }

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Minesweeper  |  Right-click to flag")
    clock = pygame.time.Clock()

    font_num   = pygame.font.SysFont("Arial", 26, bold=True)
    font_big   = pygame.font.SysFont("Consolas", 28, bold=True)
    font_small = pygame.font.SysFont("Arial", 13)

    face_rect = pygame.Rect(WIDTH // 2 - 20, TOP_BAR // 2 - 20, 40, 40)

    state = new_game()
    hover = None

    while True:
        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if my > TOP_BAR:
                    r = (my - TOP_BAR) // CELL_SIZE
                    c = mx // CELL_SIZE
                    hover = (r, c) if 0 <= r < ROWS and 0 <= c < COLS else None
                else:
                    hover = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Smiley / reset button
                if face_rect.collidepoint(mx, my):
                    state = new_game()
                    continue

                if my <= TOP_BAR or state["game_over"] or state["won"]:
                    continue

                r = (my - TOP_BAR) // CELL_SIZE
                c = mx // CELL_SIZE
                if not (0 <= r < ROWS and 0 <= c < COLS):
                    continue

                if event.button == 1:  # Left click — reveal
                    if state["flagged"][r][c] or state["revealed"][r][c]:
                        continue

                    if state["first_move"]:
                        place_mines(state["board"], r, c)
                        fill_numbers(state["board"])
                        state["first_move"] = False
                        state["start_ticks"] = pygame.time.get_ticks()

                    reveal(state["board"], state["revealed"], r, c)

                    if state["board"][r][c] == -1:
                        state["game_over"] = True
                        state["exploded"] = (r, c)
                        # Reveal all mines
                        for mr in range(ROWS):
                            for mc in range(COLS):
                                if state["board"][mr][mc] == -1:
                                    state["revealed"][mr][mc] = True
                    elif check_win(state["board"], state["revealed"]):
                        state["won"] = True

                elif event.button == 3:  # Right click — flag
                    if state["revealed"][r][c]:
                        continue
                    if state["flagged"][r][c]:
                        state["flagged"][r][c] = False
                        state["flags_placed"] -= 1
                    else:
                        state["flagged"][r][c] = True
                        state["flags_placed"] += 1

        # --- Timer ---
        if state["start_ticks"] and not state["game_over"] and not state["won"]:
            state["elapsed"] = (pygame.time.get_ticks() - state["start_ticks"]) // 1000

        # --- Face state ---
        if state["won"]:
            face_state = "win"
        elif state["game_over"]:
            face_state = "dead"
        else:
            face_state = "normal"

        mines_left = NUM_MINES - state["flags_placed"]

        # --- Draw ---
        draw_board(screen, state["board"], state["revealed"], state["flagged"],
                   hover, state["game_over"] or state["won"], state["exploded"], font_num)
        draw_top_bar(screen, mines_left, state["elapsed"], face_state, face_rect, font_big, font_small)

        if state["game_over"]:
            draw_overlay(screen, "  GAME OVER  ")
        elif state["won"]:
            draw_overlay(screen, "  YOU WIN!  ")

        pygame.display.flip()
        clock.tick(60)

main()
