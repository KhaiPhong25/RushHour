class GameUIOverlay:
    def __init__(self, font, pause_button, reset_button, select_algorithms_button, close_button):
        self.font = font
        self.pause_button = pause_button
        self.reset_button = reset_button
        self.close_button = close_button
        self.select_algorithms_button = select_algorithms_button

    def draw(self, screen):
        self.pause_button.draw(screen)
        self.reset_button.draw(screen)
        self.close_button.draw(screen)
        self.select_algorithms_button.draw(screen)
