import pygame
import sys
import button
import game_runner
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm

# Initialize PyGame and set up display
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

# Prepare the text that fades in/out on the welcome screen
text_surface = FONT.render("Click on the screen to start the game", True, (255, 255, 255))
text_surface = text_surface.convert_alpha()
text_rect = text_surface.get_rect(center = (398, 360))

alpha = 0
fade_speed = 3

# Game state flags
state_game_flag = False        # True if user is past the start screen
game_started_flag = False      # True if the game is running
paused_game_flag = False       # True if the game is paused
close_game_flag = False        # True if user requested to close game

# Toggle pause/play state and change pause button icon
def toggle_pause():
    global paused_game_flag
    paused_game_flag = not paused_game_flag

    if paused_game_flag:
        print("Pause button pressed")
        pause_button.set_icon("Images/Buttons/play.png")
    else:
        print("Play button pressed")
        pause_button.set_icon("Images/Buttons/pause.png")

# Return current pause state
def is_paused():
    return paused_game_flag

# Handle reset button press (logic can be added later)
def reset_game():
    print("Reset button pressed")

# Handle select algorithm button press (logic can be added later)
def select_algorithm():
    print("Select Algorithm button pressed")

# Close the game, reset all flags, and return to menu
def close_game():
    global state_game_flag, game_started_flag, close_game_flag, paused_game_flag, selected_level
    print("Close button pressed")
    close_game_flag = True
    state_game_flag = False
    game_started_flag = False
    paused_game_flag = False  
    selected_level = None
    pause_button.set_icon("Images/Buttons/pause.png")

# Return current close state
def is_close():
    return close_game_flag

# Create main control buttons with icons and event callbacks
close_button = button.Button(720, 20, 64, 64, "", close_game, FONT, "Images/Buttons/close.png")
pause_button = button.Button(640, 20, 64, 64, "", toggle_pause, FONT, "Images/Buttons/pause.png")
reset_button = button.Button(560, 20, 64, 64, "", reset_game, FONT, "Images/Buttons/reset.png")
select_algo_button = button.Button(480, 20, 64, 64, "", select_algorithm, FONT, "Images/Buttons/choice.png")

# Create level selection buttons with callback on click
def create_level_buttons(FONT, callback_per_level):
    buttons = []
    start_x = 255
    start_y = 295
    width = 50
    height = 50
    gap = 60
    columns = 5

    for i in range(10):
        level_number = i + 1
        x = start_x + (i % columns) * gap
        y = start_y + (i // columns) * gap

        new_button = button.Button(x, y, width, height, "", lambda lv = level_number: callback_per_level(lv), 
                                   FONT, icon_path = f"Images/Levels/level{level_number}.png")
        buttons.append(new_button)

    return buttons

# Current selected level (None if not selected yet)
selected_level = None

# When a level button is pressed, store the level and update game state
def on_level_selected(level):
    global selected_level, game_started_flag, state_game_flag
    print(f"Selected Level: {level}")
    selected_level = level
    state_game_flag = True

# Create level buttons with level selection callback
level_buttons = create_level_buttons(FONT, on_level_selected)

# Main game loop
if __name__ == "__main__":
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    state_game_flag = True  # Proceed from welcome screen

            for btn in level_buttons:
                btn.handle_event(event)

        # Welcome screen with fading text animation
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

        # Game screen after a level is selected
        else:
            file_name = f"gameboard{selected_level}"

            # Launch the game with selected search algorithm and UI components
            game_runner.Start_Game(bfs_algorithm, file_name, SCREEN, background, FONT, pause_button, 
                                reset_button, select_algo_button, close_button, is_paused, is_close)
            
            # Reset game state for returning to menu after completion or close
            game_started_flag = False
            close_game_flag = False

        # Update display and control frame rate
        pygame.display.flip()
        clock.tick(60)

    # Cleanup and exit when the game loop ends
    pygame.quit()
    sys.exit()
