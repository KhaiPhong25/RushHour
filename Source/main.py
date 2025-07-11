import pygame
import sys
import button
import config
import gameFunctions

# Initialize PyGame and configure screen
pygame.init()
SCREEN = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Rush Hour")

FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 20)
LEVEL_FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 30)
DETAIL_TITLE_FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 60)
DETAIL_FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 25)

# Load and scale background images
background = pygame.image.load("Images/welcome_screen.png")
background = pygame.transform.scale(background, (SCREEN.get_width(), SCREEN.get_height()))

level_background = pygame.image.load("Images/Levels/select_level_background.png")
level_background = pygame.transform.scale(level_background, (SCREEN.get_width(), SCREEN.get_height()))

select_algo_background = pygame.image.load("Images/Algorithms/select_algo_background.png")
select_algo_background = pygame.transform.scale(select_algo_background, (SCREEN.get_width() - 350, SCREEN.get_height() - 450))

# Set up welcome message with fade effect
text_surface = FONT.render("Click on the screen to start the game", True, (255, 255, 255))
text_surface = text_surface.convert_alpha()
text_rect = text_surface.get_rect(center = (398, 360))

alpha = 0
fade_speed = 3

# Game state flags (used for tracking game state transitions)
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


# Create control buttons
buttons = {
    # Overlay controls
    "close_algo_selector_button": button.Button(
        590, 210, 50, 50, "",
        lambda: gameFunctions.hide_algo_selector(states),
        FONT, "Images/Algorithms/close_algo_selector.png"
    ),  # Button to close the algorithm selection overlay

    # Gameplay controls
    "pause_button": button.Button(
        660, 20, 50, 50, "",
        lambda: gameFunctions.toggle_pause(states, buttons["pause_button"]),
        FONT, "Images/Buttons/pause.png"
    ),  # Pause and resume the simulation

    "reset_button": button.Button(
        600, 20, 50, 50, "",
        lambda: gameFunctions.reset_game(states),
        FONT, "Images/Buttons/reset.png"
    ),  # Reset the current game and reload the level

    "close_button": button.Button(
        720, 20, 50, 50, "",
        lambda: gameFunctions.close_game(states, buttons["pause_button"]),
        FONT, "Images/Buttons/close.png"
    ),  # Exit to level selection screen

    # Solver and algorithm control
    "select_algo_button": button.Button(
        540, 20, 50, 50, "",
        lambda: gameFunctions.select_algorithm(states),
        FONT, "Images/Buttons/choice.png"
    ),  # Open algorithm selection overlay

    "next_level_button": button.Button(
        540, 20, 50, 50, "",
        lambda: gameFunctions.next_level(states),
        FONT, "Images/Buttons/nextlevel.png"
    ),  # Advance to the next level after completion

    "view_step_button": button.Button(
        380, 480, 50, 50, "",
        lambda: gameFunctions.view_step(states),
        FONT, "Images/Buttons/viewstep.png"
    ),  # Toggle between overview and step-by-step mode

    # Information display
    "information_button": button.Button(
        20, 20, 50, 50, "",
        lambda: gameFunctions.print_details(states, SCREEN, buttons["view_step_button"], DETAIL_TITLE_FONT, DETAIL_FONT),
        FONT, "Images/Buttons/information.png"
    )  # Show game statistics and algorithm results
}


# Main game loop
if __name__ == "__main__":
    clock = pygame.time.Clock()
    running = True

    level_buttons = gameFunctions.create_level_buttons(lambda lv: gameFunctions.on_level_selected(states, lv), FONT)
    algorithm_buttons = gameFunctions.create_algorithm_buttons(states, SCREEN, FONT)

    while running:
        # Handle user input
        for event in pygame.event.get():
            running = gameFunctions.handle_events(event, states, buttons, level_buttons, algorithm_buttons)

        # Show welcome screen with fading text
        if not states["state_game_flag"]:
            alpha, fade_speed = gameFunctions.render_welcome_screen(SCREEN, background, text_surface, text_rect, alpha, fade_speed)

        # Level selection screen
        elif states["selected_level"] == 0:
            gameFunctions.render_level_selection(SCREEN, level_background, level_buttons)

        # Load level and render board
        elif states["should_load_level_flag"] and states["selected_level"] != 0:
            gameFunctions.load_and_render_level(states, SCREEN, background, buttons, LEVEL_FONT)

        # Main game simulation loop
        elif states["board_renderer"]:
            gameFunctions.render_game_simulation(states, SCREEN, background, buttons, LEVEL_FONT)

        # Draw algorithm selection overlay
        if states["show_algo_selector"]:
            gameFunctions.render_algorithm_overlay(SCREEN, select_algo_background, buttons["close_button"], algorithm_buttons)

        if states["no_solution_flag"]:
            gameFunctions.render_no_solution(states, SCREEN, DETAIL_TITLE_FONT)

        elif states["execute_algorithm_flag"]:
            gameFunctions.print_details(states, SCREEN, buttons["view_step_button"], DETAIL_TITLE_FONT, DETAIL_FONT)

        # Check if reset is triggered
        gameFunctions.handle_reset(states)

        # Check if close is triggered
        gameFunctions.handle_close(states)

        # Refresh screen and cap frame rate
        pygame.display.flip()
        clock.tick(60)

    # Exit game gracefully
    pygame.quit()
    sys.exit()
