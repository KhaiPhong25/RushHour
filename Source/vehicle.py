class Vehicle():

    # Constructor of Vehicle class
    def __init__(self, id, x, y, orientation, length):
        self.id = id                      # Unique identifier for the vehicle (e.g. 'A', 'B', '#')
        self.x = x                        # X position (column) on the grid
        self.y = y                        # Y position (row) on the grid
        self.orientation = orientation    # Orientation: 'H' for horizontal, 'V' for vertical
        self.length = int(length)         # Length of the vehicle (number of grid cells)

    # Represents the vehicle object as a string
    def __repr__(self):
        # Format: ID + X + Y + Orientation (e.g., 'A23H')
        return "'{0}{1}{2}{3}'".format(self.id, self.x, self.y, self.orientation)

    # Hash the vehicle with the representative string
    def __hash__(self):
        # Enable use of vehicle in sets or as dictionary keys
        return hash(self.__repr__())

    # Compare two hashed vehicles
    def __eq__(self, other):
        # Two vehicles are considered equal if ID, position, and orientation match
        return self.id == other.id and self.x == other.x and self.y == other.y and self.orientation == other.orientation
