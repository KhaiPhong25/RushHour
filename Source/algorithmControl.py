import pygame
import config
import helpFunctions
from path import resource_path

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

    # Draw semi-transparent overlay
    overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    # Show "Searching..." message on screen
    waiting_text_surface = FONT.render("Searching...", True, (255, 255, 255)).convert_alpha()
    waiting_text_rect = waiting_text_surface.get_rect(center = (398, 300))
    SCREEN.blit(waiting_text_surface, waiting_text_rect)
    pygame.display.flip()

    # Set current selected algorithm in state
    state["current_solver"] = algo_func
    state["selected_algorithm"] = algo_func
    state["show_algo_selector"] = False

    # Run the algorithm and store results
    if state["board_renderer"]:
        # Load game board from file based on selected level
        file_name = resource_path(f"Map/gameboard{state['selected_level']}.json")
        gameboard = helpFunctions.load_gameboard(file_name)

        # Special case for DLS algorithm (requires depth limit)
        if algo_func.__name__ == 'dls_algorithm':
            result = algo_func(gameboard, config.MAX_LIMIT)
        else:
            result = algo_func(gameboard)

        # Unpack result into game state variables
        (state["list_boardgame"], state["time_execution"], state["peak_memory"],
         state["expanded_nodes"], state["total_moves"], state["total_cost"]) = result

        # If algorithm failed to find a solution
        if not state["list_boardgame"]:
            state["no_solution_flag"] = True
            state["no_solution_time"] = pygame.time.get_ticks()
            state["execute_algorithm_flag"] = False
            return

        # Prepare to execute algorithm step-by-step
        state["current_step_index"] = 0
        state["execute_algorithm_flag"] = True
