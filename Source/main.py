import pygame
import os
import time

import helpFunctions  
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm
from gameboard import Gameboard
from vehicleSprite import VehicleSprite
from boardRenderer import BoardRenderer

if __name__ == "__main__":
    # Load the gameboard from a JSON file
    filename = "Map/gameboard1.json"
    gameboard = helpFunctions.load_gameboard(filename)

    # Choose the algorithm to solve the gameboard
    list_boardgame = A_star_algorithm(gameboard)

    # Initialize Pygame and set up the display
    pygame.init()
    screen = pygame.display.set_mode((800, 650))
    pygame.display.set_caption("Rush Hour Board Renderer")

    # Initialize the board renderer with the gameboard and image path
    list_board_renderer = []
    for i in range(len(list_boardgame)):
        list_board_renderer.append(BoardRenderer(list_boardgame[i], "Image/boardgame.png"))

    index = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen with white
        screen.fill((255, 255, 255))

        # Draw the current board state
        list_board_renderer[index].draw(screen)
        if index < len(list_boardgame) - 1:
            index += 1
        
        # Pause for half a second to visualize the steps
        time.sleep(0.5)
        #Update the display
        pygame.display.flip()

    pygame.quit()