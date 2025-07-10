import pygame
import sys
import button
import boardRenderer
import gameFunctions
import helpFunctions

# Initialize PyGame and configure screen
pygame.init()
WIDTH, HEIGHT = 800, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rush Hour")
FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 20)
DETAIL_TITLE_FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 60)
DETAIL_FONT = pygame.font.Font("Font/Gagalin-Regular.otf", 25)

# Load and scale background images
background = pygame.image.load("Images/background.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

level_background = pygame.image.load("Images/Levels/select_level_background.png")
level_background = pygame.transform.scale(level_background, (WIDTH, HEIGHT))

select_algo_background = pygame.image.load("Images/Algorithms/select_algo_background.png")
select_algo_background = pygame.transform.scale(select_algo_background, (WIDTH - 350, HEIGHT - 450))

# Set up welcome message with fade effect
text_surface = FONT.render("Click on the screen to start the game", True, (255, 255, 255))
text_surface = text_surface.convert_alpha()
text_rect = text_surface.get_rect(center = (398, 360))

alpha = 0
fade_speed = 3

# Game state flags (used for tracking game state transitions)
state = {
    "state_game_flag" : False,
    "game_started_flag" : False,
    "paused_game_flag" : False,
    "close_game_flag" : False,
    "reset_game_flag" : False,
    "start_solve_flag" : False,
    "should_load_level_flag" : False,
    "execute_algorithm_flag" : False,
    "animation_finished_flag" : False,
    "no_solution_flag" : False,
    "no_solution_time" : 0,
    "interpolating" : False,
    "interpolation_progress" : 0,
    "interpolation_frames" : 24,
    "selected_level" : 0,
    "selected_algorithm" : None,
    "current_solver" : None,
    "show_algo_selector" : False,
    "board_renderer" : None,
    "list_boardgame" : None,
    "current_step_index" : 0,
    "final_move" : 0,
    "time_execution" : 0,
    "peak_memory" : 0,
    "expanded_nodes" : 0,
    "total_moves" : None,
    "total_cost" : None
}

# Create control buttons (pause, reset, close, algorithm selection)
close_algo_selector_button = button.Button(590, 210, 50, 50, "", lambda : gameFunctions.hide_algo_selector(state), FONT, "Images/Algorithms/close_algo_selector.png")
pause_button = button.Button(660, 20, 50, 50, "", lambda : gameFunctions.toggle_pause(state, pause_button), FONT, "Images/Buttons/pause.png")
close_button = button.Button(720, 20, 50, 50, "", lambda : gameFunctions.close_game(state, pause_button), FONT, "Images/Buttons/close.png")
reset_button = button.Button(600, 20, 50, 50, "", lambda : gameFunctions.reset_game(state), FONT, "Images/Buttons/reset.png")
select_algo_button = button.Button(540, 20, 50, 50, "", lambda : gameFunctions.select_algorithm(state), FONT, "Images/Buttons/choice.png")
next_level_button = button.Button(540, 20, 50, 50, "", lambda : gameFunctions.next_level(state), FONT, "Images/Buttons/nextlevel.png")
view_step_button = button.Button(380, 480, 50, 50, "", lambda : gameFunctions.view_step(state), FONT, "Images/Buttons/viewstep.png")
information_button = button.Button(20, 20, 50, 50, "", lambda : gameFunctions.print_details(state, SCREEN, view_step_button, DETAIL_TITLE_FONT, DETAIL_FONT), FONT, "Images/Buttons/information.png")

# Main game loop
if __name__ == "__main__":
    clock = pygame.time.Clock()
    running = True

    level_buttons = gameFunctions.create_level_buttons(lambda lv: gameFunctions.on_level_selected(state, lv), FONT)
    algorithm_buttons = gameFunctions.create_algorithm_buttons(state, SCREEN, FONT)

    while running:
        # Handle user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not state["state_game_flag"]:
                    state["state_game_flag"] = True
                    continue

            # Event handling based on game state
            if state["state_game_flag"] and state["selected_level"] == 0:
                for btn in level_buttons:
                    btn.handle_event(event)

            if state["show_algo_selector"]:   
                close_algo_selector_button.handle_event(event)

                for btn in algorithm_buttons:
                    btn.handle_event(event)

            if state["selected_level"] and not state["show_algo_selector"] and not state["execute_algorithm_flag"]:
                pause_button.handle_event(event)
                reset_button.handle_event(event)

                if state["list_boardgame"]:
                    information_button.handle_event(event)

                if not state["list_boardgame"]:
                    select_algo_button.handle_event(event)

                if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]):
                        if state["selected_level"] != 0 and state["selected_level"] < 10:
                            next_level_button.handle_event(event)

                close_button.handle_event(event)                

            if state["execute_algorithm_flag"]:
                view_step_button.handle_event(event)

        # Show welcome screen with fading text
        if not state["state_game_flag"]:
            SCREEN.blit(background, (0, 0))
            alpha += fade_speed

            if alpha >= 255 or alpha <= 0:
                fade_speed = -fade_speed

            text_surface.set_alpha(alpha)
            SCREEN.blit(text_surface, text_rect)

        # Level selection screen
        elif state["selected_level"] == 0:
            SCREEN.blit(level_background, (0, 0))

            for btn in level_buttons:
                btn.draw(SCREEN)

        # Load level and render board
        elif state["should_load_level_flag"] and state["selected_level"] != 0:
            file_name = f"Map/gameboard{state['selected_level']}.json"
            gameboard = helpFunctions.load_gameboard(file_name)
            state["board_renderer"] = boardRenderer.BoardRenderer(gameboard, "Images/boardgame.png")
            state["should_load_level_flag"] = False

            SCREEN.blit(background, (0, 0))
            state["board_renderer"].draw(SCREEN)

            if state["selected_level"] != 0:
                level_text = pygame.font.Font("Font/Gagalin-Regular.otf", 30).render(f"Level {state['selected_level']}", True, "#000000")
                level_rect = level_text.get_rect(center = (WIDTH // 2, 25))
                SCREEN.blit(level_text, level_rect)

            pause_button.draw(SCREEN)
            reset_button.draw(SCREEN)
            select_algo_button.draw(SCREEN)
            close_button.draw(SCREEN)
            pygame.display.flip()

        # Main game simulation loop
        elif state["board_renderer"]:
            SCREEN.blit(background, (0, 0))

            # Step-by-step animation if not paused
            if state["start_solve_flag"] and state["list_boardgame"] and not state["paused_game_flag"]:
                # Animate interpolation between current and next state
                if not state["interpolating"] and state["current_step_index"] < len(state["list_boardgame"]) - 1:
                    state["interpolating"] = True
                    state["interpolation_progress"] = 0

                if state["interpolating"]:
                    gameFunctions.update_interpolation(state)

                # Redraw interface
                pause_button.draw(SCREEN)
                reset_button.draw(SCREEN)
                close_button.draw(SCREEN)
                information_button.draw(SCREEN)

                if not state["list_boardgame"]:
                    select_algo_button.draw(SCREEN)

                if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]):
                    next_level_button.draw(SCREEN)

                if state["animation_finished_flag"] == True:
                    if state["final_move"] < 4:
                        state["final_move"] += 1 / 480
                        state["board_renderer"].update_main_vehicle_final_animation(state["list_boardgame"][-1], state["final_move"])

                    else:
                        state["animation_finished_flag"] = False
                        state["final_move"] = 0

                    SCREEN.blit(background, (0, 0))
                    state["board_renderer"].draw(SCREEN)

                    if state["selected_level"] != 0:
                        level_text = pygame.font.Font("Font/Gagalin-Regular.otf", 30).render(f"Level {state['selected_level']}", True, "#000000")
                        level_rect = level_text.get_rect(center = (WIDTH // 2, 25))
                        SCREEN.blit(level_text, level_rect)

            # Draw board and control buttons
            state["board_renderer"].draw(SCREEN)
            if state["selected_level"] != 0:
                level_text = pygame.font.Font("Font/Gagalin-Regular.otf", 30).render(f"Level {state['selected_level']}", True, "#000000")
                level_rect = level_text.get_rect(center = (WIDTH // 2, 25))
                SCREEN.blit(level_text, level_rect)

            pause_button.draw(SCREEN)
            reset_button.draw(SCREEN)

            if state["list_boardgame"]:
                information_button.draw(SCREEN)

            if not state["list_boardgame"]:
                select_algo_button.draw(SCREEN)

            close_button.draw(SCREEN)

            if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]): 
                if state["selected_level"] != 0 and state["selected_level"] < 10:
                    next_level_button.draw(SCREEN)

        # Draw algorithm selection overlay
        if state["show_algo_selector"]:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            SCREEN.blit(overlay, (0, 0))

            bg_x = (WIDTH - select_algo_background.get_width()) // 2
            bg_y = (HEIGHT - select_algo_background.get_height()) // 2
            SCREEN.blit(select_algo_background, (bg_x, bg_y))
            close_algo_selector_button.draw(SCREEN)

            for btn in algorithm_buttons:
                btn.draw(SCREEN)

        if state["no_solution_flag"]:
            elapsed_time = pygame.time.get_ticks() - state["no_solution_time"]
            if elapsed_time < 2000:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(200)
                overlay.fill((0, 0, 0))
                SCREEN.blit(overlay, (0, 0))

                no_solution_text = DETAIL_TITLE_FONT.render("NO SOLUTION", True, "#ff4444")
                no_solution_rect = no_solution_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                SCREEN.blit(no_solution_text, no_solution_rect)

            else:
                state["no_solution_flag"] = False

        elif state["execute_algorithm_flag"]:
            gameFunctions.print_details(state, SCREEN, view_step_button, DETAIL_TITLE_FONT, DETAIL_FONT)

        # Check if reset is triggered
        if gameFunctions.is_reset(state):
            state["should_load_level_flag"] = True
            state["start_solve_flag"] = False
            state["list_boardgame"] = None

        # Check if close is triggered
        if gameFunctions.is_close(state):
            state["should_load_level_flag"] = False
            state["start_solve_flag"] = False
            state["selected_level"] = 0
            state["board_renderer"] = None
            state["close_game_flag"] = False
            state["list_boardgame"] = None

        # Refresh screen and cap frame rate
        pygame.display.flip()
        clock.tick(60)

    # Exit game gracefully
    pygame.quit()
    sys.exit()
