# GameUIOverlay manages and renders the main control buttons during gameplay
class GameUIOverlay:
    def __init__(self, font, pause_button, reset_button, select_algorithms_button, close_button):
        self.font = font
        self.pause_button = pause_button
        self.reset_button = reset_button
        self.close_button = close_button
        self.select_algorithms_button = select_algorithms_button

    # Draw all UI buttons to the game screen
    def draw(self, screen):
        self.pause_button.draw(screen)                  # Draw pause/resume button
        self.reset_button.draw(screen)                  # Draw reset button
        self.close_button.draw(screen)                  # Draw close/exit button
        self.select_algorithms_button.draw(screen)      # Draw algorithm selection button
