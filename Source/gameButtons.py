import button
import algorithmControl
import gameStates
import algorithmControl
import renderFunctions
from searchAlgorithms import bfs_algorithm, dls_algorithm, A_star_algorithm, ucs_algorithm

# Create control buttons
def create_control_buttons(states, SCREEN, FONT, DETAIL_TITLE_FONT, DETAIL_FONT):
    buttons = {
        # Overlay controls
        "close_algo_selector_button": button.Button(
            590, 210, 50, 50, "",
            lambda: algorithmControl.hide_algo_selector(states),
            FONT, "Images/Algorithms/close_algo_selector.png"
        ),  # Button to close the algorithm selection overlay

        # Gameplay controls
        "pause_button": button.Button(
            660, 20, 50, 50, "",
            lambda: gameStates.toggle_pause(states, buttons["pause_button"]),
            FONT, "Images/Buttons/pause.png"
        ),  # Pause and resume the simulation

        "reset_button": button.Button(
            600, 20, 50, 50, "",
            lambda: gameStates.reset_game(states),
            FONT, "Images/Buttons/reset.png"
        ),  # Reset the current game and reload the level

        "close_button": button.Button(
            720, 20, 50, 50, "",
            lambda: gameStates.close_game(states, buttons["pause_button"]),
            FONT, "Images/Buttons/close.png"
        ),  # Exit to level selection screen

        # Solver and algorithm control
        "select_algo_button": button.Button(
            540, 20, 50, 50, "",
            lambda: algorithmControl.select_algorithm(states),
            FONT, "Images/Buttons/choice.png"
        ),  # Open algorithm selection overlay

        "next_level_button": button.Button(
            540, 20, 50, 50, "",
            lambda: gameStates.next_level(states),
            FONT, "Images/Buttons/nextlevel.png"
        ),  # Advance to the next level after completion

        "view_step_button": button.Button(
            380, 480, 50, 50, "",
            lambda: gameStates.view_step(states),
            FONT, "Images/Buttons/viewstep.png"
        ),  # Toggle between overview and step-by-step mode

        # Information display
        "information_button": button.Button(
            20, 20, 50, 50, "",
            lambda: renderFunctions.print_details(states, SCREEN, buttons["view_step_button"], DETAIL_TITLE_FONT, DETAIL_FONT),
            FONT, "Images/Buttons/information.png"
        )  # Show game statistics and algorithm results
    }

    return buttons

# Create buttons to select algorithms
def create_algorithm_buttons(state, SCREEN, FONT):
    algorithm_buttons = []
    algorithms = ["BFS", "DLS", "UCS", "A STAR"]  # List of supported algorithms
    start_x, start_y = 210, 330  # Starting position for button grid
    width, height, gap = 80, 60, 100  # Button size and spacing

    for i, name in enumerate(algorithms):
        x = start_x + i * gap
        y = start_y

        # Create callback function for algorithm selection
        def make_callback(algo_name):
            def callback():
                func_map = {
                    "BFS": bfs_algorithm, "DLS": dls_algorithm,
                    "A STAR": A_star_algorithm, "UCS": ucs_algorithm
                }
                # Call algorithm handler with selected function
                algorithmControl.select_algorithm_callback(state, func_map[algo_name], SCREEN, FONT)
            return callback

        # Create button with icon and corresponding callback
        btn = button.Button(x, y, width, height, "", callback=make_callback(name),
                            font=FONT, icon_path=f"Images/Algorithms/{name}.png")
        algorithm_buttons.append(btn)

    return algorithm_buttons

# Create buttons for level selection
def create_level_buttons(callback, FONT):
    level_buttons = []
    start_x, start_y = 255, 295  # Starting position for button grid
    width, height, gap, columns = 50, 50, 60, 5  # Button size and layout

    for i in range(10):
        level_number = i + 1
        x = start_x + (i % columns) * gap  # Calculate X based on column
        y = start_y + (i // columns) * gap  # Calculate Y based on row

        # Create button for each level and assign level-specific callback
        btn = button.Button(x, y, width, height, "", lambda lv=level_number: callback(lv),
                            FONT, icon_path=f"Images/Levels/level{level_number}.png")
        level_buttons.append(btn)

    return level_buttons
