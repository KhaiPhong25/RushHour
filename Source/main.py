# Import necessary libraries and modules
import pygame
import sys
import button
import config
import boardRenderer
import helpFunctions
from vehicle import Vehicle
from gameboard import Gameboard
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm

# Initialize PyGame and configure screen
pygame.init()
WIDTH, HEIGHT = 800, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rush Hour")
FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 20)
DETAIL_TITLE_FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 60)
DETAIL_FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 25)

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
execute_algorithm_flag = False
animation_finished_flag = False
no_solution_flag = False
no_solution_time = 0
last_vehicle_id = '#'
interpolating = False
interpolation_progress = 0
interpolation_frames = 24

# Variables to store user selections
selected_level = 0
selected_algorithm = None
current_solver = None
show_algo_selector = False
board_renderer = None
list_boardgame = None
current_step_index = 0
final_move = 0
time_execution = 0
peak_memory = 0
expanded_nodes = 0
total_moves = None
total_cost = None

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
    global reset_game_flag, should_load_level_flag, no_solution_flag, no_solution_time
    global current_step_index, final_move, animation_finished_flag, list_boardgame
    reset_game_flag = True
    should_load_level_flag = True
    no_solution_flag = False
    no_solution_time = 0

    current_step_index = 0
    final_move = 0
    animation_finished_flag = False
    list_boardgame = None

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

# Handle algorithm button selection and initiate solving
def select_algorithm_callback(algo_func):
    global board_renderer
    SCREEN.fill('#000000')

    if board_renderer:
        board_renderer.draw(SCREEN)

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    waiting_text_surface = FONT.render("Searching...", True, (255, 255, 255))
    waiting_text_surface = waiting_text_surface.convert_alpha()
    waiting_text_rect = waiting_text_surface.get_rect(center = (398, 300))

    SCREEN.blit(waiting_text_surface, waiting_text_rect)
    pygame.display.flip()

    global current_solver, execute_algorithm_flag, selected_algorithm, list_boardgame, current_step_index, show_algo_selector
    current_solver = algo_func
    selected_algorithm = algo_func
    show_algo_selector = False

    global time_execution, peak_memory, expanded_nodes, total_moves, total_cost
    # Run selected algorithm and store the board states
    if board_renderer:
        file_name = f"Map/gameboard{selected_level}.json"
        gameboard = helpFunctions.load_gameboard(file_name)

        if algo_func.__name__ == 'dls_algorithm':
            list_boardgame, time_execution, peak_memory, expanded_nodes, total_moves, total_cost = current_solver(gameboard, config.MAX_LIMIT)
            
        else:
            list_boardgame, time_execution, peak_memory, expanded_nodes, total_moves, total_cost = current_solver(gameboard)

        if not list_boardgame or len(list_boardgame) == 0:
            global no_solution_flag, no_solution_time
            no_solution_flag = True
            no_solution_time = pygame.time.get_ticks()
            execute_algorithm_flag = False
            return

        current_step_index = 0
        execute_algorithm_flag = True


def next_level():
    global selected_level
    selected_level = selected_level + 1
    global should_load_level_flag
    should_load_level_flag = True
    global start_solve_flag
    start_solve_flag = False
    global list_boardgame
    list_boardgame = None

    global current_step_index, final_move, animation_finished_flag
    current_step_index = 0
    final_move = 0
    animation_finished_flag = False

def view_step():
    global execute_algorithm_flag, start_solve_flag 
    start_solve_flag = True
    execute_algorithm_flag = False

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
    global state_game_flag, game_started_flag, close_game_flag, paused_game_flag, selected_level, no_solution_time
    close_game_flag = True
    state_game_flag = False
    game_started_flag = False
    paused_game_flag = False
    selected_level = 0
    no_solution_time = 0
    pause_button.set_icon("Images/Buttons/pause.png")

    global current_step_index, final_move, animation_finished_flag, list_boardgame
    current_step_index = 0
    final_move = 0
    animation_finished_flag = False
    list_boardgame = None

# Check if close has been requested
def is_close():
    global close_game_flag
    return close_game_flag

# Close algorithm selector dialog
def hide_algo_selector():
    global show_algo_selector
    show_algo_selector = False

def print_details():
    global execute_algorithm_flag, start_solve_flag
    execute_algorithm_flag = True
    start_solve_flag = False
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    title_text = DETAIL_TITLE_FONT.render("DETAILS", True, "#ffffff")
    time_execution_text = DETAIL_FONT.render(f"Total time: {time_execution:.2f} seconds", True, "#ffffff")
    peak_memory_text = DETAIL_FONT.render(f"Peak memory usage: {peak_memory / (1024 * 1024):.2f} MB", True, "#ffffff")
    expanded_nodes_text = DETAIL_FONT.render(f"Total expanded nodes: {expanded_nodes}", True, "#ffffff")
    total_moves_text = DETAIL_FONT.render(f"Total moves: {total_moves}", True, "#ffffff")
    total_cost_text = DETAIL_FONT.render(f"Total cost: {total_cost}", True, "#ffffff")

    title_text_rect = (310, 100)
    time_execution_text_rect = (270, 200)
    peak_memory_text_rect = (270, 250)
    expanded_nodes_text_rect = (270, 300)
    total_moves_text_rect = (270, 350)
    total_cost_text_rect = (270, 400)

    SCREEN.blit(title_text, title_text_rect)
    SCREEN.blit(time_execution_text, time_execution_text_rect)
    SCREEN.blit(peak_memory_text, peak_memory_text_rect)
    SCREEN.blit(expanded_nodes_text, expanded_nodes_text_rect)
    SCREEN.blit(total_moves_text, total_moves_text_rect)
    SCREEN.blit(total_cost_text, total_cost_text_rect)

    view_step_button.draw(SCREEN)

# Create control buttons (pause, reset, close, algorithm selection)
close_algo_selector_button = button.Button(590, 210, 50, 50, "", lambda: hide_algo_selector(), FONT, "Images/Algorithms/close_algo_selector.png")
close_button = button.Button(720, 20, 50, 50, "", close_game, FONT, "Images/Buttons/close.png")
pause_button = button.Button(660, 20, 50, 50, "", toggle_pause, FONT, "Images/Buttons/pause.png")
reset_button = button.Button(600, 20, 50, 50, "", reset_game, FONT, "Images/Buttons/reset.png")
select_algo_button = button.Button(540, 20, 50, 50, "", select_algorithm, FONT, "Images/Buttons/choice.png")
next_level_button = button.Button(540, 20, 50, 50, "", next_level, FONT, "Images/Buttons/nextlevel.png")
view_step_button = button.Button(360, 500, 100, 50, "", view_step, FONT, "Images/Buttons/viewstep.png")
information_button = button.Button(20, 20, 50, 50, "", print_details, FONT, "Images/Buttons/information.png")

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
    selected_level = level
    state_game_flag = True
    should_load_level_flag = True

# Create all level buttons
level_buttons = create_level_buttons(FONT, on_level_selected)

def interpolate_vehicle_state(v_from, v_to, progress):
    if v_from.orientation == 'H':
        new_x = v_from.x + (v_to.x - v_from.x) * progress
        new_y = v_from.y

    else:
        new_x = v_from.x
        new_y = v_from.y + (v_to.y - v_from.y) * progress

    return Vehicle(v_from.id, new_x, new_y, v_from.orientation, v_from.length)

def interpolate_gameboard(state1, state2, progress):
    interpolated_vehicles = []

    for v1 in state1.vehicles:
        v2 = next((v for v in state2.vehicles if v.id == v1.id), None)

        if v2:
            interpolated_vehicles.append(interpolate_vehicle_state(v1, v2, progress))

        else:
            interpolated_vehicles.append(v1)

    return Gameboard(6, 6, interpolated_vehicles)

def update_interpolation():
    global interpolating, interpolation_progress, current_step_index, animation_finished_flag
    if not (interpolating and list_boardgame):
        return

    if current_step_index >= len(list_boardgame) - 1:
        interpolating = False
        current_step_index = len(list_boardgame)
        animation_finished_flag = True
        return

    state1 = list_boardgame[current_step_index]
    state2 = list_boardgame[current_step_index + 1]

    progress = interpolation_progress / interpolation_frames
    interpolated = interpolate_gameboard(state1, state2, progress)
    board_renderer.update(interpolated)

    interpolation_progress += 1
    if interpolation_progress >= interpolation_frames:
        interpolation_progress = 0
        current_step_index += 1
        if current_step_index <= len(list_boardgame) - 1:
            interpolating = True
        else:
            interpolating = False
            animation_finished_flag = True

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
            if state_game_flag and selected_level == 0:
                for btn in level_buttons:
                    btn.handle_event(event)

            if show_algo_selector:   
                close_algo_selector_button.handle_event(event)

                for btn in algorithm_buttons:
                    btn.handle_event(event)

            if selected_level and not show_algo_selector and not execute_algorithm_flag:
                pause_button.handle_event(event)
                reset_button.handle_event(event)

                if list_boardgame:
                    information_button.handle_event(event)

                if not list_boardgame:
                    select_algo_button.handle_event(event)

                if list_boardgame and current_step_index >= len(list_boardgame):
                        if selected_level != 0 and selected_level < 10:
                            next_level_button.handle_event(event)

                close_button.handle_event(event)                

            if execute_algorithm_flag:
                view_step_button.handle_event(event)

        # Show welcome screen with fading text
        if not state_game_flag:
            SCREEN.blit(background, (0, 0))
            alpha += fade_speed

            if alpha >= 255 or alpha <= 0:
                fade_speed = -fade_speed

            text_surface.set_alpha(alpha)
            SCREEN.blit(text_surface, text_rect)

        # Level selection screen
        elif selected_level == 0:
            SCREEN.blit(level_background, (0, 0))

            for btn in level_buttons:
                btn.draw(SCREEN)

        # Load level and render board
        elif should_load_level_flag and selected_level != 0:
            file_name = f"Map/gameboard{selected_level}.json"
            gameboard = helpFunctions.load_gameboard(file_name)
            board_renderer = boardRenderer.BoardRenderer(gameboard, "Images/boardgame.png")
            should_load_level_flag = False

            SCREEN.blit(background, (0, 0))
            board_renderer.draw(SCREEN)

            if selected_level != 0:
                level_text = pygame.font.Font("Font/Gagalin-Regular.otf", 30).render(f"Level {selected_level}", True, "#000000")
                level_rect = level_text.get_rect(center = (WIDTH // 2, 25))
                SCREEN.blit(level_text, level_rect)

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
                # Animate interpolation between current and next state
                if not interpolating and current_step_index < len(list_boardgame) - 1:
                    interpolating = True
                    interpolation_progress = 0
                if interpolating:
                    update_interpolation()

                # Redraw interface
                pause_button.draw(SCREEN)
                reset_button.draw(SCREEN)
                close_button.draw(SCREEN)
                information_button.draw(SCREEN)

                if not list_boardgame:
                    select_algo_button.draw(SCREEN)

                if list_boardgame and current_step_index >= len(list_boardgame):
                    next_level_button.draw(SCREEN)
                if animation_finished_flag == True:
                    if final_move < 4:
                        final_move += 1 / 480
                        board_renderer.update_main_vehicle_final_animation(list_boardgame[-1], final_move)
                    else:
                        animation_finished_flag = False
                        final_move = 0

                    SCREEN.blit(background, (0, 0))
                    board_renderer.draw(SCREEN)
                    if selected_level != 0:
                        level_text = pygame.font.Font("Font/Gagalin-Regular.otf", 30).render(f"Level {selected_level}", True, "#000000")
                        level_rect = level_text.get_rect(center = (WIDTH // 2, 25))
                        SCREEN.blit(level_text, level_rect)

            # Draw board and control buttons
            board_renderer.draw(SCREEN)
            if selected_level != 0:
                level_text = pygame.font.Font("Font/Gagalin-Regular.otf", 30).render(f"Level {selected_level}", True, "#000000")
                level_rect = level_text.get_rect(center = (WIDTH // 2, 25))
                SCREEN.blit(level_text, level_rect)
            pause_button.draw(SCREEN)
            reset_button.draw(SCREEN)

            if list_boardgame:
                information_button.draw(SCREEN)

            if not list_boardgame:
                select_algo_button.draw(SCREEN)

            close_button.draw(SCREEN)

            if list_boardgame and current_step_index >= len(list_boardgame): 
                if selected_level != 0 and selected_level < 10:
                    next_level_button.draw(SCREEN)

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

        if no_solution_flag:
            elapsed_time = pygame.time.get_ticks() - no_solution_time
            if elapsed_time < 2000:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                SCREEN.blit(overlay, (0, 0))

                no_solution_text = DETAIL_TITLE_FONT.render("NO SOLUTION", True, "#ff4444")
                no_solution_rect = no_solution_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                SCREEN.blit(no_solution_text, no_solution_rect)
            else:
                no_solution_flag = False

        elif execute_algorithm_flag:
            print_details()

        # Check if reset is triggered
        if is_reset():
            should_load_level_flag = True
            start_solve_flag = False
            list_boardgame = None

        # Check if close is triggered
        if is_close():
            should_load_level_flag = False
            start_solve_flag = False
            selected_level = 0
            board_renderer = None
            close_game_flag = False
            list_boardgame = None

        # Refresh screen and cap frame rate
        pygame.display.flip()
        clock.tick(60)

    # Exit game gracefully
    pygame.quit()
    sys.exit()
