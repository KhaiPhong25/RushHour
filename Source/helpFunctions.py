# File để chứa những hàm hỗ trợ trong quá trình code các thuật toán search ví dụ như hàm tìm Heuristic cho A*
# anh em mình cố gắng code bằng tiếng anh và cmt bằng tiếng anh luôn nha
# code tới đâu cmt tới đó nha, không cần quá chi tiết cũng được
# nhớ là phải code sạch nha Quang, cứ sau một vòng lặp hoặc một điều kiện là phải cách dòng nha Quang
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
filename = "gameboard1.json"
gameboard = load_gameboard(filename)
print(gameboard)