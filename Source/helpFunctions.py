import json
from vehicle import Vehicle
from gameboard import Gameboard
import config
from collections import deque

# Load gameboard from file .json
def load_gameboard(file_path):
    # Open the JSON file and load the vehicle data
    with open(file_path, 'r') as file:
        data =  json.load(file)

    # Create Vehicle objects from the loaded data
    vehicles = []
    for v in data:
        new_vehicle = Vehicle(id = v["id"], x = v["x"], y = v["y"], orientation = v["orientation"], length = v["length"])
        vehicles.append(new_vehicle)

    # Create the gameboard with the specified width, height, and list of vehicles
    gameboard = Gameboard(config.GAMEBOARD_WIDTH, config.GAMEBOARD_HEIGHT, vehicles)

    # Return the Gameboard object
    return gameboard

# heuristic function for A* algorithm
def heuristic_blocking_chain(gameboard):
    """
    Counts the number of distinct vehicles blocking the target vehicle's path to the exit.
    
    Input:
        game_board: The current game board state containing vehicles and layout.
        
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
        # If we find a new vehicle (not empty and different from last seen)
        if current_cell != '.' and current_cell not in blocking_vehicles:
            blocking_vehicles[current_cell] = current_cell
            to_check.append(current_cell)

    # Perform BFS on blocking vehicles to find all dependencies
    while to_check:
        blocker_id = to_check.popleft()
        blocker = vehicle_map[blocker_id]

        if blocker.orientation == "H":
            # For horizontal vehicles, check left and right neighbors
            left_pos = blocker.x - 1
            right_pos = blocker.x + blocker.length
            if left_pos >= 0 and gameboard.board[left_pos][blocker.y] != '.' and gameboard.board[left_pos][blocker.y] not in blocking_vehicles:
                to_check.append(gameboard.board[left_pos][blocker.y])
                blocking_vehicles[gameboard.board[left_pos][blocker.y]] = gameboard.board[left_pos][blocker.y]
            if right_pos <= config.GAMEBOARD_WIDTH - 1 and gameboard.board[right_pos][blocker.y] != '.' and gameboard.board[right_pos][blocker.y] not in blocking_vehicles:
                to_check.append(gameboard.board[right_pos][blocker.y])
                blocking_vehicles[gameboard.board[right_pos][blocker.y]] = gameboard.board[right_pos][blocker.y]

        else:
            # For vertical vehicles, check above and below neighbors
            above_pos = blocker.y - 1
            bottom_pos = blocker.y + blocker.length
            if above_pos >= 0 and gameboard.board[blocker.x][above_pos] != '.' and gameboard.board[blocker.x][above_pos] not in blocking_vehicles:
                to_check.append(gameboard.board[blocker.x][above_pos])
                blocking_vehicles[gameboard.board[blocker.x][above_pos]] = gameboard.board[blocker.x][above_pos]
            if bottom_pos <= config.GAMEBOARD_HEIGHT - 1 and gameboard.board[blocker.x][bottom_pos] != '.' and gameboard.board[blocker.x][bottom_pos] not in blocking_vehicles:
                to_check.append(gameboard.board[blocker.x][bottom_pos])
                blocking_vehicles[gameboard.board[blocker.x][bottom_pos]] = gameboard.board[blocker.x][bottom_pos]

    return len(blocking_vehicles)

#trace back solution
def trace_back_solution(visited_list, initial_state, goal_state):
    if goal_state == initial_state: 
        return goal_state
    
    result = []
    current_state = goal_state
    
    while current_state != initial_state:
        result.append(current_state)
        parent = visited_list[current_state][-1]
        current_state = parent

    result.append(initial_state)
    result.reverse()
    return result