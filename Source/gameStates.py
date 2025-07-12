import pygame
from path import resource_path

# Game state flags (used for tracking game state transitions)
def create_game_state():
    states = {
        # Game flow flags
        "state_game_flag": False,          # Whether the game has moved past the welcome screen
        "game_started_flag": False,        # Whether the game has started
        "paused_game_flag": False,         # Whether the game is currently paused
        "close_game_flag": False,          # Flag indicating a request to close the current game
        "reset_game_flag": False,          # Flag indicating a request to reset the game
        "start_solve_flag": False,         # Whether the auto-solve animation should begin
        "should_load_level_flag": False,   # Whether a level needs to be loaded after selection
        "execute_algorithm_flag": False,   # Whether an algorithm is currently being executed
        "show_algo_selector": False,       # Whether the algorithm selection overlay is visible

        # Level, algorithm and solver selection
        "selected_level": 0,               # Currently selected level (0 means not selected)
        "selected_algorithm": None,        # Name of the selected algorithm
        "current_solver": None,            # Reference to the algorithm function being used

        # Board and animation rendering
        "board_renderer": None,            # Object that draws the game board
        "interpolating": False,            # Whether interpolation is happening between states
        "interpolation_progress": 0,       # Current progress of the interpolation (0.0 to 1.0)
        "interpolation_frames": 24,        # Number of frames to animate between each move
        "animation_finished_flag": False,  # Whether final animation has completed
        "final_move": 0,                   # Animation progress value for final winning move

        # Solution data 
        "list_boardgame": None,            # List of board states representing the full solution path
        "current_step_index": 0,           # Index of the current solution step being displayed
        "time_execution": 0,               # Time taken to compute the solution
        "peak_memory": 0,                  # Peak memory used during the solving process
        "expanded_nodes": 0,               # Total number of nodes expanded during solving
        "total_moves": None,               # Total number of moves in the solution
        "total_cost": None,                # Total cost of the solution (if applicable)

        # No solution state
        "no_solution_flag": False,         # Whether the algorithm failed to find a solution
        "no_solution_time": 0              # Timestamp when the "NO SOLUTION" state was triggered
    }

    return states

# Toggle pause/resume and update pause/play icon
def toggle_pause(state, pause_button):
    state["paused_game_flag"] = not state["paused_game_flag"]
    pause_button.set_icon(resource_path("Images/Buttons/play.png") if state["paused_game_flag"] else resource_path("Images/Buttons/pause.png"))

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
    pause_button.set_icon(resource_path("Images/Buttons/pause.png"))

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

# Step-by-step view toggle
def view_step(state):
    state["start_solve_flag"] = True
    state["execute_algorithm_flag"] = False

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

# Handle all mouse and quit events
def handle_events(event, state, buttons, level_buttons, algorithm_buttons):
    # Handle window close
    if event.type == pygame.QUIT:
        return False

    # Handle click to start from welcome screen
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if not state["state_game_flag"]:
            state["state_game_flag"] = True
            return True

    # Handle level selection screen
    if state["state_game_flag"] and state["selected_level"] == 0:
        for btn in level_buttons:
            btn.handle_event(event)

    # Handle algorithm selector overlay
    if state["show_algo_selector"]:
        buttons["close_algo_selector_button"].handle_event(event)
        for btn in algorithm_buttons:
            btn.handle_event(event)

    # Handle in-game button events
    if state["selected_level"] and not state["show_algo_selector"] and not state["execute_algorithm_flag"]:
        buttons["pause_button"].handle_event(event)
        buttons["reset_button"].handle_event(event)

        # If solution exists, show info
        if state["list_boardgame"]:
            buttons["information_button"].handle_event(event)
        else:
            buttons["select_algo_button"].handle_event(event)

        # If finished, enable next level
        if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]):
            if state["selected_level"] != 0 and state["selected_level"] < 10:
                buttons["next_level_button"].handle_event(event)

        buttons["close_button"].handle_event(event)

    # If algorithm is running, allow switching to step view
    if state["execute_algorithm_flag"]:
        buttons["view_step_button"].handle_event(event)

    return True
