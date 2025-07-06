import pygame
import sys
import button
import config
import boardRenderer
import helpFunctions
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm

# Initialize PyGame and configure screen
pygame.init()
WIDTH, HEIGHT = 800, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rush Hour")
FONT = pygame.font.SysFont("", 30, bold = True)

# Load and scale background images
background = pygame.image.load("Images/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

level_background = pygame.image.load("Images/Levels/select_level_background.png")
level_background = pygame.transform.scale(level_background, (WIDTH, HEIGHT))

# Set up welcome message with fade effect
text_surface = FONT.render("Click on the screen to start the game", True, (255, 255, 255))
text_surface = text_surface.convert_alpha()
text_rect = text_surface.get_rect(center = (398, 360))

alpha = 0
fade_speed = 3

# Game state flags
state_game_flag = False
game_started_flag = False
paused_game_flag = False
close_game_flag = False
reset_game_flag = False
start_solve_flag = False
should_load_level_flag = False

# Selection variables
selected_level = None
selected_algorithm = None
current_solver = None
show_algo_selector = False
board_renderer = None
list_boardgame = []
current_step_index = 0

# Toggle pause/resume and update icon
def toggle_pause():
    global paused_game_flag
    paused_game_flag = not paused_game_flag
    pause_button.set_icon("Images/Buttons/play.png" if paused_game_flag else "Images/Buttons/pause.png")

# Check if game is paused
def is_paused():
    global paused_game_flag
    return paused_game_flag

# Trigger reset and reload level
def reset_game():
    global reset_game_flag, should_load_level_flag
    print("Reset game pressed")
    reset_game_flag = True
    should_load_level_flag = True

# Check and reset reset flag
def is_reset():
    global reset_game_flag

    if reset_game_flag:
        reset_game_flag = False
        return True
    
    return False

# Display algorithm selection overlay
def select_algorithm():
    global show_algo_selector
    show_algo_selector = True

# Handle algorithm button selection
def select_algorithm_callback(algo_func):
    global current_solver, show_algo_selector, start_solve_flag, selected_algorithm, list_boardgame, current_step_index
    print(f"Selected algorithm: {algo_func.__name__}")
    current_solver = algo_func
    selected_algorithm = algo_func
    show_algo_selector = False

    if board_renderer:
        file_name = f"Map/gameboard{selected_level}.json"
        gameboard = helpFunctions.load_gameboard(file_name)

        if algo_func.__name__ == 'dls_algorithm':
            list_boardgame = current_solver(gameboard, config.MAX_LIMIT)

        else:
            list_boardgame = current_solver(gameboard)

        current_step_index = 0
        start_solve_flag = True

# Create algorithm selection buttons
algorithm_buttons = []
def create_algorithm_buttons(font):
    global algorithm_buttons
    algorithms = [("BFS", bfs_algorithm), ("DLS", dls_algorithm), ("A*", A_star_algorithm), ("UCS", ucs_algorithm)]
    start_x, start_y, width, height, gap = 260, 250, 280, 50, 65

    buttons = []
    for i, (name, func) in enumerate(algorithms):
        def make_callback(f):
            return lambda: select_algorithm_callback(f)
        
        btn = button.Button(start_x, start_y + i * gap, width, height, text = name, 
                            callback = make_callback(func), font = font)
        buttons.append(btn)

    algorithm_buttons = buttons

create_algorithm_buttons(FONT)

# Close the game and reset relevant flags
def close_game():
    global state_game_flag, game_started_flag, close_game_flag, paused_game_flag, selected_level
    print("Close button pressed")
    close_game_flag = True
    state_game_flag = False
    game_started_flag = False
    paused_game_flag = False
    selected_level = None
    pause_button.set_icon("Images/Buttons/pause.png")

# Check if close has been requested
def is_close():
    global close_game_flag
    return close_game_flag

# Create control buttons
close_button = button.Button(720, 20, 64, 64, "", close_game, FONT, "Images/Buttons/close.png")
pause_button = button.Button(640, 20, 64, 64, "", toggle_pause, FONT, "Images/Buttons/pause.png")
reset_button = button.Button(560, 20, 64, 64, "", reset_game, FONT, "Images/Buttons/reset.png")
select_algo_button = button.Button(480, 20, 64, 64, "", select_algorithm, FONT, "Images/Buttons/choice.png")

# Generate level selection buttons
def create_level_buttons(font, callback):
    buttons = []
    start_x, start_y, width, height, gap, columns = 255, 295, 50, 50, 60, 5

    for i in range(10):
        level_number = i + 1
        x = start_x + (i % columns) * gap
        y = start_y + (i // columns) * gap
        btn = button.Button(x, y, width, height, "", lambda lv = level_number: callback(lv),
                            font, icon_path = f"Images/Levels/level{level_number}.png")
        buttons.append(btn)

    return buttons

# Handle level selection
def on_level_selected(level):
    global selected_level, state_game_flag, should_load_level_flag
    print(f"Selected Level: {level}")
    selected_level = level
    state_game_flag = True
    should_load_level_flag = True

# Create all level buttons
level_buttons = create_level_buttons(FONT, on_level_selected)

# Main game loop
if __name__ == "__main__":
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not state_game_flag:
                    state_game_flag = True
                    continue
            
            if state_game_flag and selected_level is None:
                for btn in level_buttons:
                    btn.handle_event(event)

            if show_algo_selector:
                for btn in algorithm_buttons:
                    btn.handle_event(event)

            pause_button.handle_event(event)
            reset_button.handle_event(event)
            select_algo_button.handle_event(event)
            close_button.handle_event(event)

        # Show welcome screen
        if not state_game_flag:
            SCREEN.blit(background, (0, 0))
            alpha += fade_speed

            if alpha >= 255 or alpha <= 0:
                fade_speed = -fade_speed

            text_surface.set_alpha(alpha)
            SCREEN.blit(text_surface, text_rect)

        # Show level selection screen
        elif selected_level is None:
            SCREEN.blit(level_background, (0, 0))

            for btn in level_buttons:
                btn.draw(SCREEN)

        # Load level when flagged
        elif should_load_level_flag and selected_level is not None:
            file_name = f"Map/gameboard{selected_level}.json"
            gameboard = helpFunctions.load_gameboard(file_name)
            board_renderer = boardRenderer.BoardRenderer(gameboard, "Images/boardgame.png")
            should_load_level_flag = False

            SCREEN.blit(background, (0, 0))
            board_renderer.draw(SCREEN)
            pause_button.draw(SCREEN)
            reset_button.draw(SCREEN)
            select_algo_button.draw(SCREEN)
            close_button.draw(SCREEN)
            pygame.display.flip()

        # Run simulation if board is ready
        elif board_renderer:
            SCREEN.blit(background, (0, 0))

            # Step-by-step animation if not paused
            if start_solve_flag and list_boardgame and not paused_game_flag:
                if current_step_index < len(list_boardgame):
                    board_renderer.update(list_boardgame[current_step_index])
                    current_step_index += 1
                    pygame.time.delay(250)

            # Always draw current board state and controls
            board_renderer.draw(SCREEN)
            pause_button.draw(SCREEN)
            reset_button.draw(SCREEN)
            select_algo_button.draw(SCREEN)
            close_button.draw(SCREEN)

        # Draw algorithm selection overlay
        if show_algo_selector:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            SCREEN.blit(overlay, (0, 0))
            pygame.draw.rect(SCREEN, (255, 255, 255), (240, 220, 320, 300), border_radius=10)
            title = FONT.render("Select Algorithm", True, (0, 0, 0))
            SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 230))
            
            for btn in algorithm_buttons:
                btn.draw(SCREEN)

        # If reset is requested, reload board
        if is_reset():
            should_load_level_flag = True
            start_solve_flag = False

        # If game is closed, reset board and selections
        if is_close():
            should_load_level_flag = False
            start_solve_flag = False
            selected_level = None
            board_renderer = None
            close_game_flag = False

        # Refresh screen and cap frame rate
        pygame.display.flip()
        clock.tick(60)

    # Exit game gracefully
    pygame.quit()
    sys.exit()
