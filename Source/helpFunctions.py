import json
from vehicle import Vehicle
from gameboard import Gameboard

def load_gameboard(file_name):
    # Define the board size (fixed at 6x6 for this project)
    width = 6
    height = 6

    # Open the JSON file and load the vehicle data
    with open(file_name, 'r') as file:
        data =  json.load(file)

    # Create Vehicle objects from the loaded data
    vehicles = []
    for v in data:
        new_vehicle = Vehicle(id = v["id"], x = v["x"], y = v["y"], orientation = v["orientation"], length = v["length"])
        vehicles.append(new_vehicle)

    # Create the gameboard with the specified width, height, and list of vehicles
    gameboard = Gameboard(width, height, vehicles)

    # Return the Gameboard object
    return gameboard

# heuristic function for A* algorithm
def number_blocking_vehicle(game_board):
    """
    Counts the number of distinct vehicles blocking the target vehicle's path to the exit.
    
    Input:
        game_board: The current game board state containing vehicles and layout.
        
    Output:
        int: Number of unique vehicles blocking the target vehicle's right path.
    """
    result = 0
    vehicles = gameboard.vehicles

    # The target vehicle is assumed to be the first in the list (typically the red car)
    target_vehicle = vehicles[0]

    # Get target vehicle's rightmost position 
    y_position = target_vehicle.y
    x_position = target_vehicle.x + target_vehicle.length - 1

    # Track last seen vehicle to avoid double-counting the same vehicle
    last_character = '.' # '.' represents empty space

    # Scan all cells to the right of the target vehicle
    for col in range(x_position + 1, game_board.width):
        current_cell = game_board.board[y_position][col]
        # If we find a new vehicle (not empty and different from last seen)
        if current_cell != '.' and current_cell != last_character:
            result += 1
            last_character = current_cell # Remember this vehicle to avoid recounting
    
    return result

#trace back solution
def trace_back_solution(visited_list, initial_state, goal_state):
    if goal_state == initial_state: return goal_state
    result = []
    current_state = goal_state
    while current_state != initial_state:
        result.append(current_state)
        parent = visited_list[hash(current_state)][-1]
        current_state = parent

    result.reverse()
    return result

def print_solution_path(path):
    for i in range(len(path)):
        print(path[i])
        print('\n \n')

    print(len(path))

# In ra để check Gameboard
filename = "RushHour/Map/gameboard3.json"
gameboard = load_gameboard(filename)
print(gameboard)
print (gameboard.vehicles)
print(number_blocking_vehicle(gameboard))