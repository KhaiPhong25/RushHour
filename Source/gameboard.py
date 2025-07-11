import math
from vehicle import Vehicle

class Gameboard():

    # Constructor of Gameboard class
    def __init__(self, width, height, vehicles):
        self.width = width                # Width of the game board
        self.height = height              # Height of the game board

        # Fill the board grid with empty cells represented by '.'
        self.board = [["." for x in range(self.width)] for y in range(self.height)]
        self.vehicles = vehicles          # List of Vehicle objects

        # Place vehicles on the board
        for vehicle in self.vehicles:
            # Place horizontal vehicle
            if vehicle.orientation == 'H':
                for i in range(vehicle.length):
                    self.board[int(vehicle.y)][int(vehicle.x + i)] = vehicle.id
            # Place vertical vehicle
            if vehicle.orientation == 'V':
                for i in range(vehicle.length):
                    self.board[int(vehicle.y + i)][int(vehicle.x)] = vehicle.id

        # Sort vehicles in matrix order (top to bottom, left to right)
        self.vehicles = sorted(vehicles, key=lambda v: (v.y, v.x))

    # Represents the gameboard object as a string
    def __repr__(self):
        # Format the board for printing with spacing
        self.printableboard = '\n\n'.join(['      '.join(['{}'.format(item) for item in row]) for row in self.board])
        return self.printableboard

    # Hash the gameboard using its string representation
    def __hash__(self):
        return hash(self.__repr__())

    # Compare two gameboard objects based on vehicle positions and IDs
    def __eq__(self, other):
        for v in self.vehicles:
            if v not in other.vehicles: 
                return False
        return True

    # Generate all possible board states from valid vehicle movements
    def check_for_moves(self):
        # Initialize list to hold all valid next board states
        possibleBoards = []

        # Iterate through each vehicle
        for vehicle in self.vehicles:
            x_position = int(vehicle.x)
            y_position = int(vehicle.y)

            # Horizontal movement checks
            if vehicle.orientation == 'H':
                # Move left
                if x_position != 0:
                    if self.board[y_position][x_position - 1] == '.':
                        newVehicles = self.vehicles.copy()
                        newVehicle = Vehicle(vehicle.id, x_position - 1, y_position, vehicle.orientation, vehicle.length)
                        newVehicles.remove(vehicle)
                        newVehicles.append(newVehicle)
                        possibleBoards.append(newVehicles)

                # Move right
                if (x_position + vehicle.length - 1) != self.width - 1:
                    if self.board[y_position][x_position + vehicle.length] == '.':
                        newVehicles = self.vehicles.copy()
                        newVehicle = Vehicle(vehicle.id, x_position + 1, y_position, vehicle.orientation, vehicle.length)
                        newVehicles.remove(vehicle)
                        newVehicles.append(newVehicle)
                        possibleBoards.append(newVehicles)

            # Vertical movement checks
            if vehicle.orientation == 'V':
                # Move up
                if y_position != 0:
                    if self.board[y_position - 1][x_position] == '.':
                        newVehicles = self.vehicles.copy()
                        newVehicle = Vehicle(vehicle.id, x_position, y_position - 1, vehicle.orientation, vehicle.length)
                        newVehicles.remove(vehicle)
                        newVehicles.append(newVehicle)
                        possibleBoards.append(newVehicles)

                # Move down
                if y_position + (vehicle.length - 1) != self.height - 1:
                    if self.board[y_position + vehicle.length][x_position] == '.':
                        newVehicles = self.vehicles.copy()
                        newVehicle = Vehicle(vehicle.id, x_position, y_position + 1, vehicle.orientation, vehicle.length)
                        newVehicles.remove(vehicle)
                        newVehicles.append(newVehicle)
                        possibleBoards.append(newVehicles)

        # Return all generated next states
        return possibleBoards

    # Return the solution path from a given state (used for debugging or placeholder)
    def get_solution_path(self, state):
        return state

    # Check if the red car (usually represented by '#') has reached the exit
    def has_solved(self):
        for vehicle in self.vehicles:
            # Define the target exit position for red car
            winning_x = self.width - 2
            winning_y = math.ceil(self.height / 2) - 1

            # Check if red car is in the correct position and orientation
            if vehicle.id == '#' and vehicle.x == winning_x and vehicle.y == winning_y and vehicle.orientation == "H":
                return True

        return False
