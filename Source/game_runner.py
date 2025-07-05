import pygame
import time
import helpFunctions
from boardRenderer import BoardRenderer
from overlayUI import GameUIOverlay

def Start_Game(solver, file_name, SCREEN, background, FONT, pause_button, 
               reset_button, select_algo_button, close_button, is_paused, is_close):
    file_path = f"Map/{file_name}.json"
    gameboard = helpFunctions.load_gameboard(file_path)

    list_boardgame = solver(gameboard)
    board_renderer = BoardRenderer(gameboard, "Images/boardgame.png")

    ui_overlay = GameUIOverlay(FONT, pause_button, reset_button, select_algo_button, close_button)

    index = 0
    clock = pygame.time.Clock()

    while index < len(list_boardgame) and not is_close():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            pause_button.handle_event(event)
            reset_button.handle_event(event)
            close_button.handle_event(event)
            select_algo_button.handle_event(event)

        SCREEN.blit(background, (0, 0))
        
        if not is_paused():
            board_renderer.update(list_boardgame[index])
            board_renderer.draw(SCREEN)
            ui_overlay.draw(SCREEN)
            pygame.display.update()
            time.sleep(0.5)
            index += 1

        else:
            # Khi đang pause vẫn vẽ lại frame hiện tại
            board_renderer.draw(SCREEN)
            ui_overlay.draw(SCREEN)
            pygame.display.update()

        clock.tick(60)
