# Import necessary libraries and modules
import pygame
import sys
import button
import config
import boardRenderer
import helpFunctions
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm
import time

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

select_algo_background = pygame.image.load("Images/Algorithms/select_algo_background.png")
select_algo_background = pygame.transform.scale(select_algo_background, (WIDTH - 350, HEIGHT - 450))

# Set up welcome message with fade effect
text_surface = FONT.render("Click on the screen to start the game", True, (255, 255, 255))
text_surface = text_surface.convert_alpha()
text_rect = text_surface.get_rect(center = (398, 360))

alpha = 0
fade_speed = 3

# Game state flags (used for tracking game state transitions)
state_game_flag = False
game_started_flag = False
paused_game_flag = False
close_game_flag = False
reset_game_flag = False
start_solve_flag = False
should_load_level_flag = False

# Variables to store user selections
selected_level = None
selected_algorithm = None
current_solver = None
show_algo_selector = False
board_renderer = None
list_boardgame = []
current_step_index = 0
final_move = 1

# Toggle pause/resume and update icon
def toggle_pause():
    global paused_game_flag
    print("Pause/Play game pressed")
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
    print("Algorithms selector pressed")
    show_algo_selector = True

# Handle algorithm button selection and initiate solving
def select_algorithm_callback(algo_func):
    global current_solver, show_algo_selector, start_solve_flag, selected_algorithm, list_boardgame, current_step_index
    print(f"Selected algorithm: {algo_func.__name__}")
    current_solver = algo_func
    selected_algorithm = algo_func
    show_algo_selector = False

    # Run selected algorithm and store the board states
    if board_renderer:
        file_name = f"Map/gameboard{selected_level}.json"
        gameboard = helpFunctions.load_gameboard(file_name)

        if algo_func.__name__ == 'dls_algorithm':
            list_boardgame = current_solver(gameboard, config.MAX_LIMIT)
        else:
            list_boardgame = current_solver(gameboard)

        current_step_index = 0
        start_solve_flag = True

# Create buttons for selecting search algorithms
algorithm_buttons = []
def create_algorithm_buttons(font):
    global algorithm_buttons
    algorithms = ["BFS", "DLS", "UCS", "A STAR"]
    start_x, start_y = 210, 330  # Position to center the row
    width, height, gap = 80, 60, 100

    buttons = []
    for i, name in enumerate(algorithms):
        x = start_x + i * gap
        y = start_y

        # Wrap callback in closure to capture algorithm correctly
        def make_callback(algo_name):
            def callback():
                func_map = {"BFS": bfs_algorithm, "DLS": dls_algorithm, 
                            "A STAR": A_star_algorithm, "UCS": ucs_algorithm}
                select_algorithm_callback(func_map[algo_name])
            return callback

        btn = button.Button(x, y, width, height, "", callback = make_callback(name),
                            font=font, icon_path = f"Images/Algorithms/{name}.png")
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

# Close algorithm selector dialog
def hide_algo_selector():
    global show_algo_selector
    print("Close algorithms selector pressed")
    show_algo_selector = False

# Create control buttons (pause, reset, close, algorithm selection)
close_algo_selector_button = button.Button(590, 210, 50, 50, "", lambda: hide_algo_selector(), FONT, "Images/Algorithms/close_algo_selector.png")
close_button = button.Button(720, 20, 50, 50, "", close_game, FONT, "Images/Buttons/close.png")
pause_button = button.Button(660, 20, 50, 50, "", toggle_pause, FONT, "Images/Buttons/pause.png")
reset_button = button.Button(600, 20, 50, 50, "", reset_game, FONT, "Images/Buttons/reset.png")
select_algo_button = button.Button(540, 20, 50, 50, "", select_algorithm, FONT, "Images/Buttons/choice.png")

# Generate level selection buttons (1-10)
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
        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not state_game_flag:
                    state_game_flag = True
                    continue

            # Event handling based on game state
            if state_game_flag and selected_level is None:
                for btn in level_buttons:
                    btn.handle_event(event)

            if show_algo_selector:
                if not paused_game_flag:
                    toggle_pause()
                
                else:    
                    close_algo_selector_button.handle_event(event)
                    for btn in algorithm_buttons:
                        btn.handle_event(event)

            if not show_algo_selector:
                pause_button.handle_event(event)
                reset_button.handle_event(event)
                select_algo_button.handle_event(event)
                close_button.handle_event(event)

        # Show welcome screen with fading text
        if not state_game_flag:
            SCREEN.blit(background, (0, 0))
            alpha += fade_speed
            if alpha >= 255 or alpha <= 0:
                fade_speed = -fade_speed
            text_surface.set_alpha(alpha)
            SCREEN.blit(text_surface, text_rect)

        # Level selection screen
        elif selected_level is None:
            SCREEN.blit(level_background, (0, 0))
            for btn in level_buttons:
                btn.draw(SCREEN)

        # Load level and render board
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

        # Main game simulation loop
        elif board_renderer:
            SCREEN.blit(background, (0, 0))

            # Step-by-step animation if not paused
            if start_solve_flag and list_boardgame and not paused_game_flag:
                if current_step_index < len(list_boardgame):
                    board_renderer.update(list_boardgame[current_step_index])
                    current_step_index += 1
                    pygame.time.delay(250)

                else:
                    # Final animation for winning condition
                    if final_move < 6:
                        board_renderer.update_main_vehicle_final_animation(list_boardgame[current_step_index - 1], final_move)
                        final_move += 1
                        pygame.time.delay(120)
                    else:
                        final_move = 1

            # Draw board and control buttons
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

            bg_x = (WIDTH - select_algo_background.get_width()) // 2
            bg_y = (HEIGHT - select_algo_background.get_height()) // 2
            SCREEN.blit(select_algo_background, (bg_x, bg_y))
            close_algo_selector_button.draw(SCREEN)
            for btn in algorithm_buttons:
                btn.draw(SCREEN)

        # Check if reset is triggered
        if is_reset():
            should_load_level_flag = True
            start_solve_flag = False

        # Check if close is triggered
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
