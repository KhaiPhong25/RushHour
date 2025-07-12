import pygame
import sys
from Code import config
from Code import gameStates
from Code import gameButtons
from Code import renderFunctions

# Initialize PyGame and configure screen
pygame.init()
SCREEN = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
pygame.display.set_caption("Rush Hour")

# Load game fonts
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

# Main game loop
if __name__ == "__main__":
    clock = pygame.time.Clock()
    running = True

    # Initialize game states and UI buttons
    states = gameStates.create_game_state()
    buttons = gameButtons.create_control_buttons(states, SCREEN, FONT, DETAIL_TITLE_FONT, DETAIL_FONT)

    # Create level and algorithm selection buttons
    level_buttons = gameButtons.create_level_buttons(lambda lv: gameStates.on_level_selected(states, lv), FONT)
    algorithm_buttons = gameButtons.create_algorithm_buttons(states, SCREEN, FONT)

    # Start game loop
    while running:
        # Handle user input
        for event in pygame.event.get():
            running = gameStates.handle_events(event, states, buttons, level_buttons, algorithm_buttons)

        # Show welcome screen with fading text
        if not states["state_game_flag"]:
            alpha, fade_speed = renderFunctions.render_welcome_screen(SCREEN, background, text_surface, text_rect, alpha, fade_speed)

        # Level selection screen
        elif states["selected_level"] == 0:
            renderFunctions.render_level_selection(SCREEN, level_background, level_buttons)

        # Load level and render board
        elif states["should_load_level_flag"] and states["selected_level"] != 0:
            renderFunctions.load_and_render_level(states, SCREEN, background, buttons, LEVEL_FONT)

        # Main game simulation loop
        elif states["board_renderer"]:
            renderFunctions.render_game_simulation(states, SCREEN, background, buttons, LEVEL_FONT)

        # Draw algorithm selection overlay
        if states["show_algo_selector"]:
            renderFunctions.render_algorithm_overlay(SCREEN, select_algo_background, buttons["close_algo_selector_button"], algorithm_buttons)

        # Show "No solution found" message if applicable
        if states["no_solution_flag"]:
            renderFunctions.render_no_solution(states, SCREEN, DETAIL_TITLE_FONT)

        # Display algorithm execution details
        elif states["execute_algorithm_flag"]:
            renderFunctions.print_details(states, SCREEN, buttons["view_step_button"], DETAIL_TITLE_FONT, DETAIL_FONT)

        # Check if reset is triggered
        gameStates.handle_reset(states)

        # Check if close is triggered
        gameStates.handle_close(states)

        # Refresh screen and cap frame rate
        pygame.display.flip()
        clock.tick(60)

    # Exit game gracefully
    pygame.quit()
    sys.exit()
