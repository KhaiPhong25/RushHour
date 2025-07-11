import pygame
import button
import config
import helpFunctions
import boardRenderer
from vehicle import Vehicle
from gameboard import Gameboard
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm

# Pause, Resume, and Game Flow Control

# Toggle pause/resume and update pause/play icon
def toggle_pause(state, pause_button):
    state["paused_game_flag"] = not state["paused_game_flag"]
    pause_button.set_icon("Images/Buttons/play.png" if state["paused_game_flag"] else "Images/Buttons/pause.png")

# Check if game is currently paused
def is_paused(state):
    return state["paused_game_flag"]

# Request to reset the game and reload the level
def reset_game(state):
    state["reset_game_flag"] = True
    state["should_load_level_flag"] = True
    state["no_solution_flag"] = False
    state["no_solution_time"] = 0
    state["current_step_index"] = 0
    state["final_move"] = 0
    state["animation_finished_flag"] = False
    state["list_boardgame"] = None

# Check if reset was requested; if so, reset the flag
def is_reset(state):
    if state["reset_game_flag"]:
        state["reset_game_flag"] = False

        return True
    
    return False

# Request to close the game and reset related flags
def close_game(state, pause_button):
    state["close_game_flag"] = True
    state["state_game_flag"] = False
    state["game_started_flag"] = False
    state["paused_game_flag"] = False
    state["selected_level"] = 0
    state["no_solution_time"] = 0
    state["current_step_index"] = 0
    state["final_move"] = 0
    state["animation_finished_flag"] = False
    state["list_boardgame"] = None
    pause_button.set_icon("Images/Buttons/pause.png")

# Check if close was requested
def is_close(state):
    return state["close_game_flag"]

# Helper to process the reset logic
def handle_reset(state):
    if is_reset(state):
        state["should_load_level_flag"] = True
        state["start_solve_flag"] = False
        state["list_boardgame"] = None

# Helper to process the close logic
def handle_close(state):
    if is_close(state):
        state["should_load_level_flag"] = False
        state["start_solve_flag"] = False
        state["selected_level"] = 0
        state["board_renderer"] = None
        state["close_game_flag"] = False
        state["list_boardgame"] = None

# Algorithm Selection and Execution

# Display algorithm selector overlay
def select_algorithm(state):
    state["show_algo_selector"] = True

# Hide algorithm selector overlay
def hide_algo_selector(state):
    state["show_algo_selector"] = False

# Trigger solving using selected algorithm
def select_algorithm_callback(state, algo_func, SCREEN, FONT):
    # Render waiting UI
    SCREEN.fill('#000000')
    if state["board_renderer"]:
        state["board_renderer"].draw(SCREEN)

    overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    waiting_text_surface = FONT.render("Searching...", True, (255, 255, 255)).convert_alpha()
    waiting_text_rect = waiting_text_surface.get_rect(center=(398, 300))
    SCREEN.blit(waiting_text_surface, waiting_text_rect)
    pygame.display.flip()

    # Set state
    state["current_solver"] = algo_func
    state["selected_algorithm"] = algo_func
    state["show_algo_selector"] = False

    # Run the algorithm and store results
    if state["board_renderer"]:
        file_name = f"Map/gameboard{state['selected_level']}.json"
        gameboard = helpFunctions.load_gameboard(file_name)

        if algo_func.__name__ == 'dls_algorithm':
            result = algo_func(gameboard, config.MAX_LIMIT)

        else:
            result = algo_func(gameboard)

        (state["list_boardgame"], state["time_execution"], state["peak_memory"],
         state["expanded_nodes"], state["total_moves"], state["total_cost"]) = result

        if not state["list_boardgame"]:
            state["no_solution_flag"] = True
            state["no_solution_time"] = pygame.time.get_ticks()
            state["execute_algorithm_flag"] = False

            return

        state["current_step_index"] = 0
        state["execute_algorithm_flag"] = True

# Step-by-step view toggle
def view_step(state):
    state["start_solve_flag"] = True
    state["execute_algorithm_flag"] = False

# Level Management

# Move to the next level
def next_level(state):
    state["selected_level"] += 1
    state["should_load_level_flag"] = True
    state["start_solve_flag"] = False
    state["list_boardgame"] = None
    state["current_step_index"] = 0
    state["final_move"] = 0
    state["animation_finished_flag"] = False

# When level is selected from level menu
def on_level_selected(state, level):
    state["selected_level"] = level
    state["state_game_flag"] = True
    state["should_load_level_flag"] = True

# Button and Event Handling

# Create buttons to select algorithms
def create_algorithm_buttons(state, SCREEN, FONT):
    algorithm_buttons = []
    algorithms = ["BFS", "DLS", "UCS", "A STAR"]
    start_x, start_y = 210, 330
    width, height, gap = 80, 60, 100

    for i, name in enumerate(algorithms):
        x = start_x + i * gap
        y = start_y

        def make_callback(algo_name):
            def callback():
                func_map = {
                    "BFS": bfs_algorithm, "DLS": dls_algorithm,
                    "A STAR": A_star_algorithm, "UCS": ucs_algorithm
                }
                select_algorithm_callback(state, func_map[algo_name], SCREEN, FONT)
            return callback

        btn = button.Button(x, y, width, height, "", callback=make_callback(name),
                            font=FONT, icon_path=f"Images/Algorithms/{name}.png")
        algorithm_buttons.append(btn)

    return algorithm_buttons

# Create buttons for level selection
def create_level_buttons(callback, FONT):
    level_buttons = []
    start_x, start_y = 255, 295
    width, height, gap, columns = 50, 50, 60, 5

    for i in range(10):
        level_number = i + 1
        x = start_x + (i % columns) * gap
        y = start_y + (i // columns) * gap
        btn = button.Button(x, y, width, height, "", lambda lv=level_number: callback(lv),
                            FONT, icon_path=f"Images/Levels/level{level_number}.png")
        level_buttons.append(btn)

    return level_buttons

# Handle all mouse and quit events
def handle_events(event, state, buttons, level_buttons, algorithm_buttons):
    if event.type == pygame.QUIT:
        return False

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not state["state_game_flag"]:
            state["state_game_flag"] = True
            return True

    if state["state_game_flag"] and state["selected_level"] == 0:
        for btn in level_buttons:
            btn.handle_event(event)

    if state["show_algo_selector"]:
        buttons["close_algo_selector_button"].handle_event(event)
        for btn in algorithm_buttons:
            btn.handle_event(event)

    if state["selected_level"] and not state["show_algo_selector"] and not state["execute_algorithm_flag"]:
        buttons["pause_button"].handle_event(event)
        buttons["reset_button"].handle_event(event)

        if state["list_boardgame"]:
            buttons["information_button"].handle_event(event)

        else:
            buttons["select_algo_button"].handle_event(event)

        if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]):
            if state["selected_level"] != 0 and state["selected_level"] < 10:
                buttons["next_level_button"].handle_event(event)

        buttons["close_button"].handle_event(event)

    if state["execute_algorithm_flag"]:
        buttons["view_step_button"].handle_event(event)

    return True

# Interpolation & Animation

# Update gameboard interpolation for smooth movement
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

# Rendering Functions

# Render welcome screen with fade-in text
def render_welcome_screen(SCREEN, background, text_surface, text_rect, alpha, fade_speed):
    SCREEN.blit(background, (0, 0))
    alpha += fade_speed

    if alpha >= 255 or alpha <= 0:
        fade_speed = -fade_speed

    text_surface.set_alpha(alpha)
    SCREEN.blit(text_surface, text_rect)

    return alpha, fade_speed

# Render level selection screen
def render_level_selection(SCREEN, level_background, level_buttons):
    SCREEN.blit(level_background, (0, 0))

    for btn in level_buttons:
        btn.draw(SCREEN)

# Render algorithm selection overlay
def render_algorithm_overlay(SCREEN, select_algo_background, close_button, algorithm_buttons):
    overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    bg_x = (SCREEN.get_width() - select_algo_background.get_width()) // 2
    bg_y = (SCREEN.get_height() - select_algo_background.get_height()) // 2
    SCREEN.blit(select_algo_background, (bg_x, bg_y))

    close_button.draw(SCREEN)

    for btn in algorithm_buttons:
        btn.draw(SCREEN)

# Show NO SOLUTION overlay
def render_no_solution(state, SCREEN, DETAIL_TITLE_FONT):
    elapsed_time = pygame.time.get_ticks() - state["no_solution_time"]

    if elapsed_time < 2000:
        overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        SCREEN.blit(overlay, (0, 0))
        no_solution_text = DETAIL_TITLE_FONT.render("NO SOLUTION", True, "#ff4444")
        rect = no_solution_text.get_rect(center=(SCREEN.get_width() // 2, SCREEN.get_height() // 2))
        SCREEN.blit(no_solution_text, rect)
    
    else:
        state["no_solution_flag"] = False

# Print statistics after solving
def print_details(state, SCREEN, view_step_button, DETAIL_TITLE_FONT, DETAIL_FONT):
    state["execute_algorithm_flag"] = True
    state["start_solve_flag"] = False

    overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    y_start = 200
    spacing = 50

    entries = [
        ("DETAILS", DETAIL_TITLE_FONT, 100),
        (f"Total time: {state['time_execution']:.2f} seconds", DETAIL_FONT, y_start),
        (f"Peak memory usage: {state['peak_memory'] / (1024 * 1024):.2f} MB", DETAIL_FONT, y_start + spacing),
        (f"Total expanded nodes: {state['expanded_nodes']}", DETAIL_FONT, y_start + 2 * spacing),
        (f"Total moves: {state['total_moves']}", DETAIL_FONT, y_start + 3 * spacing),
        (f"Total cost: {state['total_cost']}", DETAIL_FONT, y_start + 4 * spacing),
    ]

    for text, font, y in entries:
        surface = font.render(text, True, "#ffffff")
        SCREEN.blit(surface, (270, y))

    view_step_button.draw(SCREEN)

# Load level and render initial state
def load_and_render_level(state, SCREEN, background, buttons, FONT):
    file_name = f"Map/gameboard{state['selected_level']}.json"
    gameboard = helpFunctions.load_gameboard(file_name)
    state["board_renderer"] = boardRenderer.BoardRenderer(gameboard, "Images/boardgame.png")
    state["should_load_level_flag"] = False

    SCREEN.blit(background, (0, 0))
    state["board_renderer"].draw(SCREEN)

    if state["selected_level"] != 0:
        level_text = FONT.render(f"Level {state['selected_level']}", True, "#000000")
        rect = level_text.get_rect(center=(SCREEN.get_width() // 2, 25))
        SCREEN.blit(level_text, rect)

    buttons["pause_button"].draw(SCREEN)
    buttons["reset_button"].draw(SCREEN)
    buttons["select_algo_button"].draw(SCREEN)
    buttons["close_button"].draw(SCREEN)
    pygame.display.flip()

# Render full game simulation state
def render_game_simulation(state, SCREEN, background, buttons, FONT):
    SCREEN.blit(background, (0, 0))

    if state["start_solve_flag"] and state["list_boardgame"] and not state["paused_game_flag"]:
        if not state["interpolating"] and state["current_step_index"] < len(state["list_boardgame"]) - 1:
            state["interpolating"] = True
            state["interpolation_progress"] = 0

        if state["interpolating"]:
            update_interpolation(state)

        buttons["pause_button"].draw(SCREEN)
        buttons["reset_button"].draw(SCREEN)
        buttons["close_button"].draw(SCREEN)
        buttons["information_button"].draw(SCREEN)

        if not state["list_boardgame"]:
            buttons["select_algo_button"].draw(SCREEN)

        if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]):
            buttons["next_level_button"].draw(SCREEN)

        if state["animation_finished_flag"]:
            if state["final_move"] < 4:
                state["final_move"] += 1 / 480
                state["board_renderer"].update_main_vehicle_final_animation(state["list_boardgame"][-1], state["final_move"])
            
            else:
                state["animation_finished_flag"] = False
                state["final_move"] = 0

            SCREEN.blit(background, (0, 0))
            state["board_renderer"].draw(SCREEN)

            if state["selected_level"] != 0:
                level_text = FONT.render(f"Level {state['selected_level']}", True, "#000000")
                rect = level_text.get_rect(center=(SCREEN.get_width() // 2, 25))
                SCREEN.blit(level_text, rect)

    state["board_renderer"].draw(SCREEN)
    if state["selected_level"] != 0:
        level_text = FONT.render(f"Level {state['selected_level']}", True, "#000000")
        rect = level_text.get_rect(center=(SCREEN.get_width() // 2, 25))
        SCREEN.blit(level_text, rect)

    buttons["pause_button"].draw(SCREEN)
    buttons["reset_button"].draw(SCREEN)

    if state["list_boardgame"]:
        buttons["information_button"].draw(SCREEN)

    else:
        buttons["select_algo_button"].draw(SCREEN)

    buttons["close_button"].draw(SCREEN)

    if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]) and state["selected_level"] < 10:
        buttons["next_level_button"].draw(SCREEN)