import pygame
import sys
import button
import game_runner
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm

# Initialize PyGame
pygame.init()
WIDTH, HEIGHT = 800, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rush Hour")
FONT = pygame.font.SysFont("", 30, bold = True)

# Load background
background = pygame.image.load("Images/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Text fade in/out
text_surface = FONT.render("Click on the screen to start the game", True, (255, 255, 255))
text_surface = text_surface.convert_alpha()
text_rect = text_surface.get_rect(center = (398, 360))

alpha = 0
fade_speed = 3

# Flag
state_game_flag = False
game_started_flag = False
paused_game_flag = False
close_game_flag = False

def toggle_pause():
    global paused_game_flag
    paused_game_flag = not paused_game_flag

    if paused_game_flag:
        print("Pause button pressed")
        pause_button.set_icon("Images/Buttons/play.png")
    else:
        print("Play button pressed")
        pause_button.set_icon("Images/Buttons/pause.png")

def is_paused():
    return paused_game_flag

def reset_game():
    print("Reset button pressed")

def select_algorithm():
    print("Select Algorithm button pressed")

def close_game():
    global state_game_flag, game_started_flag, close_game_flag, paused_game_flag
    print("Close button pressed")
    close_game_flag = True
    state_game_flag = False
    game_started_flag = False
    paused_game_flag = False  
    pause_button.set_icon("Images/Buttons/pause.png")

def is_close():
    return close_game_flag

close_button = button.Button(720, 20, 64, 64, None, close_game, FONT, "Images/Buttons/close.png")
pause_button = button.Button(640, 20, 64, 64, None, toggle_pause, FONT, "Images/Buttons/pause.png")
reset_button = button.Button(560, 20, 64, 64, None, reset_game, FONT, "Images/Buttons/reset.png")
select_algo_button = button.Button(480, 20, 64, 64, None, select_algorithm, FONT, "Images/Buttons/choice.png")

# Main loop
if __name__ == "__main__":
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 1 = left mouse
                    state_game_flag = True

        if not state_game_flag:
            SCREEN.blit(background, (0, 0))
            alpha += fade_speed

            if alpha >= 255 or alpha <= 0:
                fade_speed = -fade_speed

            text_surface.set_alpha(alpha)
            SCREEN.blit(text_surface, text_rect)

        elif not game_started_flag:
            SCREEN.blit(background, (0, 0))  # clear background
            game_runner.Start_Game(bfs_algorithm, "gameboard1", SCREEN, background, FONT, pause_button, 
                                reset_button, select_algo_button, close_button, is_paused, is_close)
            
            game_started_flag = False
            close_game_flag = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()
