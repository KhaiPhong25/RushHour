import pygame
import button
import config
import helpFunctions
from vehicle import Vehicle
from gameboard import Gameboard
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm

WIDTH, HEIGHT = 800, 650

# Toggle pause/resume and update icon
def toggle_pause(state, pause_button):
    state["paused_game_flag"] = not state["paused_game_flag"]
    pause_button.set_icon("Images/Buttons/play.png" if state["paused_game_flag"] else "Images/Buttons/pause.png")

# Check if game is paused
def is_paused(state):
    return state["paused_game_flag"]

# Trigger reset and reload level
def reset_game(state):
    state["reset_game_flag"] = True
    state["should_load_level_flag"] = True
    state["no_solution_flag"] = False
    state["no_solution_time"] = 0

    state["current_step_index"] = 0
    state["final_move"] = 0
    state["animation_finished_flag"] = False
    state["list_boardgame"] = None

# Check and reset reset flag
def is_reset(state):
    if state["reset_game_flag"]:
        state["reset_game_flag"] = False
        return True
    
    return False

# Display algorithm selection overlay
def select_algorithm(state):
    state["show_algo_selector"] = True

# Handle algorithm button selection and initiate solving
def select_algorithm_callback(state, algo_func, SCREEN, FONT):
    SCREEN.fill('#000000')

    if state["board_renderer"]:
        state["board_renderer"].draw(SCREEN)

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    waiting_text_surface = FONT.render("Searching...", True, (255, 255, 255))
    waiting_text_surface = waiting_text_surface.convert_alpha()
    waiting_text_rect = waiting_text_surface.get_rect(center = (398, 300))

    SCREEN.blit(waiting_text_surface, waiting_text_rect)
    pygame.display.flip()

    state["current_solver"] = algo_func
    state["selected_algorithm"] = algo_func
    state["show_algo_selector"] = False

    # Run selected algorithm and store the board states
    if state["board_renderer"]:
        file_name = f"Map/gameboard{state['selected_level']}.json"
        gameboard = helpFunctions.load_gameboard(file_name)

        if algo_func.__name__ == 'dls_algorithm':
            state["list_boardgame"], state["time_execution"], state["peak_memory"], state["expanded_nodes"], state["total_moves"], state["total_cost"] = state["current_solver"](gameboard, config.MAX_LIMIT)
            
        else:
            state["list_boardgame"], state["time_execution"], state["peak_memory"], state["expanded_nodes"], state["total_moves"], state["total_cost"] = state["current_solver"](gameboard)

        if not state["list_boardgame"] or len(state["list_boardgame"]) == 0:
            state["no_solution_flag"] = True
            state["no_solution_time"] = pygame.time.get_ticks()
            state["execute_algorithm_flag"] = False
            return

        state["current_step_index"] = 0
        state["execute_algorithm_flag"] = True


def next_level(state):
    state["selected_level"] = state["selected_level"] + 1
    state["should_load_level_flag"] = True
    state["start_solve_flag"] = False
    state["list_boardgame"] = None
    state["current_step_index"] = 0
    state["final_move"] = 0
    state["animation_finished_flag"] = False

def view_step(state):
    state["start_solve_flag"] = True
    state["execute_algorithm_flag"] = False

# Create buttons for selecting search algorithms
def create_algorithm_buttons(state, SCREEN, FONT):
    algorithm_buttons = []

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
                select_algorithm_callback(state, func_map[algo_name], SCREEN, FONT)

            return callback

        btn = button.Button(x, y, width, height, "", callback = make_callback(name),
                            font = FONT, icon_path = f"Images/Algorithms/{name}.png")
        buttons.append(btn)

    algorithm_buttons = buttons

    return algorithm_buttons

# Close the game and reset relevant flags
def close_game(state, pause_button):
    state["close_game_flag"] = True
    state["state_game_flag"] = False
    state["game_started_flag"] = False
    state["paused_game_flag"] = False
    state["selected_level"] = 0
    state["no_solution_time"] = 0
    pause_button.set_icon("Images/Buttons/pause.png")

    state["current_step_index"] = 0
    state["final_move"] = 0
    state["animation_finished_flag"] = False
    state["list_boardgame"] = None

# Check if close has been requested
def is_close(state):
    return state["close_game_flag"]

# Close algorithm selector dialog
def hide_algo_selector(state):
    state["show_algo_selector"] = False

def print_details(state, SCREEN, view_step_button, DETAIL_TITLE_FONT, DETAIL_FONT):
    state["execute_algorithm_flag"] = True
    state["start_solve_flag"] = False

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    title_text = DETAIL_TITLE_FONT.render("DETAILS", True, "#ffffff")
    time_execution_text = DETAIL_FONT.render(f"Total time: {state["time_execution"]:.2f} seconds", True, "#ffffff")
    peak_memory_text = DETAIL_FONT.render(f"Peak memory usage: {state["peak_memory"] / (1024 * 1024):.2f} MB", True, "#ffffff")
    expanded_nodes_text = DETAIL_FONT.render(f"Total expanded nodes: {state["expanded_nodes"]}", True, "#ffffff")
    total_moves_text = DETAIL_FONT.render(f"Total moves: {state["total_moves"]}", True, "#ffffff")
    total_cost_text = DETAIL_FONT.render(f"Total cost: {state["total_cost"]}", True, "#ffffff")

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

# Generate level selection buttons (1-10)
def create_level_buttons(callback, FONT):
    level_buttons = []
    start_x, start_y, width, height, gap, columns = 255, 295, 50, 50, 60, 5

    for i in range(10):
        level_number = i + 1
        x = start_x + (i % columns) * gap
        y = start_y + (i // columns) * gap
        btn = button.Button(x, y, width, height, "", lambda lv = level_number: callback(lv),
                            FONT, icon_path = f"Images/Levels/level{level_number}.png")
        level_buttons.append(btn)

    return level_buttons

# Handle level selection
def on_level_selected(state, level):
    state["selected_level"] = level
    state["state_game_flag"] = True
    state["should_load_level_flag"] = True

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

def update_interpolation(state):
    if not (state["interpolating"] and state["list_boardgame"]):
        return

    if state["current_step_index"] >= len(state["list_boardgame"]) - 1:
        state["interpolating"] = False
        state["current_step_index"] = len(state["list_boardgame"])
        state["animation_finished_flag"] = True
        return

    state1 = state["list_boardgame"][state["current_step_index"]]
    state2 = state["list_boardgame"][state["current_step_index"] + 1]

    progress = state["interpolation_progress"] / state["interpolation_frames"]
    interpolated = interpolate_gameboard(state1, state2, progress)
    state["board_renderer"].update(interpolated)

    state["interpolation_progress"] += 1
    if state["interpolation_progress"] >= state["interpolation_frames"]:
        state["interpolation_progress"] = 0
        state["current_step_index"] += 1

        if state["current_step_index"] <= len(state["list_boardgame"]) - 1:
            state["interpolating"] = True

        else:
            state["interpolating"] = False
            state["animation_finished_flag"] = True