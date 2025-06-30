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

# In ra để check Gameboard
filename = ".//Map//gameboard1.json"
gameboard = load_gameboard(filename)
print(gameboard)