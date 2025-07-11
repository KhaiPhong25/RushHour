import config
from vehicle import Vehicle
from gameboard import Gameboard

# Update gameboard interpolation for smooth movement
def update_interpolation(state):
    # Return early if interpolation is not active or no solution path exists
    if not (state["interpolating"] and state["list_boardgame"]):
        return

    # Stop interpolation if at the end of the solution path
    if state["current_step_index"] >= len(state["list_boardgame"]) - 1:
        state["interpolating"] = False
        state["current_step_index"] = len(state["list_boardgame"])
        state["animation_finished_flag"] = True
        return

    # Get current and next board states
    state1 = state["list_boardgame"][state["current_step_index"]]
    state2 = state["list_boardgame"][state["current_step_index"] + 1]

    # Calculate interpolation progress (from 0.0 to 1.0)
    progress = state["interpolation_progress"] / state["interpolation_frames"]

    # Create interpolated board between current and next state
    interpolated = interpolate_gameboard(state1, state2, progress)

    # Update renderer with interpolated state
    state["board_renderer"].update(interpolated)

    # Advance interpolation progress
    state["interpolation_progress"] += 1
    if state["interpolation_progress"] >= state["interpolation_frames"]:
        # Move to next step in path
        state["interpolation_progress"] = 0
        state["current_step_index"] += 1

        # If not at end, continue interpolation
        if state["current_step_index"] <= len(state["list_boardgame"]) - 1:
            state["interpolating"] = True
        else:
            # End of path reached
            state["interpolating"] = False
            state["animation_finished_flag"] = True

# Interpolate individual vehicle position between two states
def interpolate_vehicle_state(v_from, v_to, progress):
    # Horizontal movement interpolation
    if v_from.orientation == 'H':
        new_x = v_from.x + (v_to.x - v_from.x) * progress
        new_y = v_from.y
    else:
        # Vertical movement interpolation
        new_x = v_from.x
        new_y = v_from.y + (v_to.y - v_from.y) * progress

    # Return new vehicle object with interpolated position
    return Vehicle(v_from.id, new_x, new_y, v_from.orientation, v_from.length)

# Interpolate entire board state between two steps
def interpolate_gameboard(state1, state2, progress):
    interpolated_vehicles = []

    # For each vehicle in the current state
    for v1 in state1.vehicles:
        # Find the corresponding vehicle in the next state
        v2 = next((v for v in state2.vehicles if v.id == v1.id), None)

        # Interpolate position if found in both states
        if v2:
            interpolated_vehicles.append(interpolate_vehicle_state(v1, v2, progress))
        else:
            # Keep same vehicle if not moved
            interpolated_vehicles.append(v1)

    # Return new gameboard with interpolated vehicles
    return Gameboard(config.GAMEBOARD_WIDTH, config.GAMEBOARD_HEIGHT, interpolated_vehicles)
