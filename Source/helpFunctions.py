import json
import config
from vehicle import Vehicle
from gameboard import Gameboard
from collections import deque

# Load gameboard from file .json
def load_gameboard(file_path):
    # Open the JSON file and load the vehicle data
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Create Vehicle objects from the loaded data
    vehicles = []
    for v in data:
        new_vehicle = Vehicle(id=v["id"], x=v["x"], y=v["y"], orientation=v["orientation"], length=v["length"])
        vehicles.append(new_vehicle)

    # Create the gameboard with the specified width, height, and list of vehicles
    gameboard = Gameboard(config.GAMEBOARD_WIDTH, config.GAMEBOARD_HEIGHT, vehicles)

    # Return the Gameboard object
    return gameboard

# Heuristic function for A* algorithm
def heuristic_blocking_chain(gameboard):
    """
    Counts the number of distinct vehicles blocking the target vehicle's path to the exit.

    Input:
        gameboard: The current game board state containing vehicles and layout.

    Output:
        int: Number of unique vehicles that form a chain block
    """

    vehicles = gameboard.vehicles

    # Create a quick lookup dictionary: vehicle ID -> Vehicle object
    vehicle_map = {v.id: v for v in vehicles}

    # Get the red car (target vehicle) by ID "#"
    target_vehicle = vehicle_map["#"]

    # Get target vehicle's rightmost position 
    y_position = target_vehicle.y
    x_position = target_vehicle.x + target_vehicle.length - 1

    to_check = deque()
    blocking_vehicles = {}

    # Scan all cells to the right of the target vehicle
    for col in range(x_position + 1, gameboard.width):
        current_cell = gameboard.board[y_position][col]

        # If we find a new vehicle (not empty and not already counted)
        if current_cell != '.' and current_cell not in blocking_vehicles:
            blocking_vehicles[current_cell] = current_cell
            to_check.append(current_cell)

    # Perform BFS on blocking vehicles to find all dependent blockers
    while to_check:
        blocker_id = to_check.popleft()
        blocker = vehicle_map[blocker_id]

        if blocker.orientation == "H":
            # For horizontal vehicles, check left and right adjacent cells
            left_pos = blocker.x - 1
            right_pos = blocker.x + blocker.length

            if left_pos >= 0:
                neighbor = gameboard.board[blocker.y][left_pos]
                if neighbor != '.' and neighbor not in blocking_vehicles:
                    to_check.append(neighbor)
                    blocking_vehicles[neighbor] = neighbor

            if right_pos <= config.GAMEBOARD_WIDTH - 1:
                neighbor = gameboard.board[blocker.y][right_pos]
                if neighbor != '.' and neighbor not in blocking_vehicles:
                    to_check.append(neighbor)
                    blocking_vehicles[neighbor] = neighbor

        else:
            # For vertical vehicles, check above and below adjacent cells
            above_pos = blocker.y - 1
            bottom_pos = blocker.y + blocker.length

            if above_pos >= 0:
                neighbor = gameboard.board[above_pos][blocker.x]
                if neighbor != '.' and neighbor not in blocking_vehicles:
                    to_check.append(neighbor)
                    blocking_vehicles[neighbor] = neighbor

            if bottom_pos <= config.GAMEBOARD_HEIGHT - 1:
                neighbor = gameboard.board[bottom_pos][blocker.x]
                if neighbor != '.' and neighbor not in blocking_vehicles:
                    to_check.append(neighbor)
                    blocking_vehicles[neighbor] = neighbor

    # Return the number of unique blocking vehicles
    return len(blocking_vehicles)

# Trace back the path from goal state to initial state
def trace_back_solution(visited_list, initial_state, goal_state):
    # If goal equals initial state, return it directly
    if goal_state == initial_state:
        return goal_state

    result = []
    current_state = goal_state

    # Traverse backwards from goal to initial using parent pointers
    while current_state != initial_state:
        result.append(current_state)
        parent = visited_list[current_state][-1]
        current_state = parent

    # Add initial state and reverse the path to correct order
    result.append(initial_state)
    result.reverse()

    return result
