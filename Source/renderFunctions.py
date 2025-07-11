import pygame
import helpFunctions
import boardRenderer
import transition

# Render welcome screen with fade-in text
def render_welcome_screen(SCREEN, background, text_surface, text_rect, alpha, fade_speed):
    SCREEN.blit(background, (0, 0))  # Draw background image
    alpha += fade_speed  # Update alpha value for fading effect

    # Reverse fade direction at boundaries
    if alpha >= 255 or alpha <= 0:
        fade_speed = -fade_speed

    text_surface.set_alpha(alpha)  # Apply updated alpha to text
    SCREEN.blit(text_surface, text_rect)  # Draw fading text

    return alpha, fade_speed  # Return updated values for next frame

# Render level selection screen
def render_level_selection(SCREEN, level_background, level_buttons):
    SCREEN.blit(level_background, (0, 0))  # Draw background

    # Draw each level selection button
    for btn in level_buttons:
        btn.draw(SCREEN)

# Render algorithm selection overlay
def render_algorithm_overlay(SCREEN, select_algo_background, close_button, algorithm_buttons):
    # Draw semi-transparent dark overlay
    overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    # Draw algorithm selector background image centered
    bg_x = (SCREEN.get_width() - select_algo_background.get_width()) // 2
    bg_y = (SCREEN.get_height() - select_algo_background.get_height()) // 2
    SCREEN.blit(select_algo_background, (bg_x, bg_y))

    close_button.draw(SCREEN)  # Draw close button

    # Draw algorithm option buttons
    for btn in algorithm_buttons:
        btn.draw(SCREEN)

# Show NO SOLUTION overlay
def render_no_solution(state, SCREEN, DETAIL_TITLE_FONT):
    elapsed_time = pygame.time.get_ticks() - state["no_solution_time"]  # Time since flag was set

    if elapsed_time < 2000:
        # Draw dark overlay
        overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        SCREEN.blit(overlay, (0, 0))

        # Display "NO SOLUTION" message
        no_solution_text = DETAIL_TITLE_FONT.render("NO SOLUTION", True, "#ff4444")
        rect = no_solution_text.get_rect(center=(SCREEN.get_width() // 2, SCREEN.get_height() // 2))
        SCREEN.blit(no_solution_text, rect)
    
    else:
        # Clear flag after timeout
        state["no_solution_flag"] = False

# Print statistics after solving
def print_details(state, SCREEN, view_step_button, DETAIL_TITLE_FONT, DETAIL_FONT):
    state["execute_algorithm_flag"] = True  # Switch to detail view
    state["start_solve_flag"] = False       # Stop animation

    # Draw dark overlay background
    overlay = pygame.Surface((SCREEN.get_width(), SCREEN.get_height()))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    SCREEN.blit(overlay, (0, 0))

    # Layout parameters
    title_y = 130
    spacing = 45
    line_start_y = title_y + 80

    # List of information entries to show
    entries = [
        ("DETAILS", DETAIL_TITLE_FONT, title_y),
        (f"Algorithm: {state['selected_algorithm'].__name__.replace('_', ' ').upper()}", DETAIL_FONT, line_start_y),
        (f"Total time: {state['time_execution']:.2f} seconds", DETAIL_FONT, line_start_y + spacing),
        (f"Peak memory usage: {state['peak_memory'] / (1024 * 1024):.2f} MB", DETAIL_FONT, line_start_y + spacing * 2),
        (f"Total expanded nodes: {state['expanded_nodes']}", DETAIL_FONT, line_start_y + spacing * 3),
        (f"Total moves: {state['total_moves']}", DETAIL_FONT, line_start_y + spacing * 4),
        (f"Total cost: {state['total_cost']}", DETAIL_FONT, line_start_y + spacing * 5),
    ]

    # Render each entry to screen
    for text, font, y in entries:
        surface = font.render(text, True, "#ffffff")
        rect = surface.get_rect(center=(SCREEN.get_width() // 2, y))
        SCREEN.blit(surface, rect)

    view_step_button.draw(SCREEN)  # Show step-by-step button

# Load level and render initial state
def load_and_render_level(state, SCREEN, background, buttons, FONT):
    # Load gameboard from file
    file_name = f"Map/gameboard{state['selected_level']}.json"
    gameboard = helpFunctions.load_gameboard(file_name)
    state["board_renderer"] = boardRenderer.BoardRenderer(gameboard, "Images/boardgame.png")
    state["should_load_level_flag"] = False

    # Draw background and board
    SCREEN.blit(background, (0, 0))
    state["board_renderer"].draw(SCREEN)

    # Display level title
    if state["selected_level"] != 0:
        level_text = FONT.render(f"Level {state['selected_level']}", True, "#000000")
        rect = level_text.get_rect(center=(SCREEN.get_width() // 2, 25))
        SCREEN.blit(level_text, rect)

    # Draw top control buttons
    buttons["pause_button"].draw(SCREEN)
    buttons["reset_button"].draw(SCREEN)
    buttons["select_algo_button"].draw(SCREEN)
    buttons["close_button"].draw(SCREEN)

    pygame.display.flip()  # Update screen

# Render full game simulation state
def render_game_simulation(state, SCREEN, background, buttons, FONT):
    SCREEN.blit(background, (0, 0))  # Clear background

    # Handle automatic step transition during simulation
    if state["start_solve_flag"] and state["list_boardgame"] and not state["paused_game_flag"]:
        # Begin interpolation between current and next step
        if not state["interpolating"] and state["current_step_index"] < len(state["list_boardgame"]) - 1:
            state["interpolating"] = True
            state["interpolation_progress"] = 0

        # Perform transition animation
        if state["interpolating"]:
            transition.update_interpolation(state)

        # Draw controls and info during simulation
        buttons["pause_button"].draw(SCREEN)
        buttons["reset_button"].draw(SCREEN)
        buttons["close_button"].draw(SCREEN)
        buttons["information_button"].draw(SCREEN)

        if not state["list_boardgame"]:
            buttons["select_algo_button"].draw(SCREEN)

        # Show next level button if level completed
        if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]):
            buttons["next_level_button"].draw(SCREEN)

        # Final winning animation for red car
        if state["animation_finished_flag"]:
            if state["final_move"] < 4:
                state["final_move"] += 1 / 480
                state["board_renderer"].update_main_vehicle_final_animation(state["list_boardgame"][-1], state["final_move"])
            else:
                state["animation_finished_flag"] = False
                state["final_move"] = 0

            SCREEN.blit(background, (0, 0))
            state["board_renderer"].draw(SCREEN)

            if state["selected_level"] != 0:
                level_text = FONT.render(f"Level {state['selected_level']}", True, "#000000")
                rect = level_text.get_rect(center=(SCREEN.get_width() // 2, 25))
                SCREEN.blit(level_text, rect)

    # Always draw the board state
    state["board_renderer"].draw(SCREEN)
    if state["selected_level"] != 0:
        level_text = FONT.render(f"Level {state['selected_level']}", True, "#000000")
        rect = level_text.get_rect(center=(SCREEN.get_width() // 2, 25))
        SCREEN.blit(level_text, rect)

    # Draw control buttons
    buttons["pause_button"].draw(SCREEN)
    buttons["reset_button"].draw(SCREEN)

    if state["list_boardgame"]:
        buttons["information_button"].draw(SCREEN)
    else:
        buttons["select_algo_button"].draw(SCREEN)

    buttons["close_button"].draw(SCREEN)

    # Show next level if solution is complete
    if state["list_boardgame"] and state["current_step_index"] >= len(state["list_boardgame"]) and state["selected_level"] < 10:
        buttons["next_level_button"].draw(SCREEN)
