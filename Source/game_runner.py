import pygame
import time
import helpFunctions
from boardRenderer import BoardRenderer
from overlayUI import GameUIOverlay

# Start_Game initializes and runs the gameplay animation using the selected algorithm
def Start_Game(solver, file_name, SCREEN, background, FONT, pause_button, 
               reset_button, select_algo_button, close_button, is_paused, is_close):

    # Build the path to the level configuration file
    file_path = f"Map/{file_name}.json"
    
    # Load the game board configuration from JSON file
    gameboard = helpFunctions.load_gameboard(file_path)

    # Generate the solution path using the selected algorithm
    list_boardgame = solver(gameboard)

    # Create board renderer with the game state and background image
    board_renderer = BoardRenderer(gameboard, "Images/boardgame.png")

    # Initialize UI overlay to display buttons
    ui_overlay = GameUIOverlay(FONT, pause_button, reset_button, select_algo_button, close_button)

    index = 0  # Current step in the solution path
    clock = pygame.time.Clock()  # For controlling frame rate

    # Game rendering loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Quit the game if window is closed
                pygame.quit()
                exit()
            
            # Handle UI button events
            pause_button.handle_event(event)
            reset_button.handle_event(event)
            select_algo_button.handle_event(event)
            close_button.handle_event(event)

        # Draw background on the screen
        SCREEN.blit(background, (0, 0))

        # Check if close button was triggered
        if is_close():
            break  
        
        # Check if pause button pressed
        if not is_paused():
            if index < len(list_boardgame):
                # Update board state to current step
                board_renderer.update(list_boardgame[index])
                board_renderer.draw(SCREEN)
                ui_overlay.draw(SCREEN)
                pygame.display.update()
                
                # Pause between steps to visualize movement
                time.sleep(0.5)
                index += 1

            else:
                # Animation finished — show the final (goal) state indefinitely
                board_renderer.draw(SCREEN)
                ui_overlay.draw(SCREEN)
                pygame.display.update()
        else:
            # Game is paused — redraw current frame without advancing
            board_renderer.draw(SCREEN)
            ui_overlay.draw(SCREEN)
            pygame.display.update()

        # Maintain consistent frame rate
        clock.tick(60)
