class Vehicle():

    # Constructor of Vehicle class
    def __init__(self, id, x, y, orientation, length):
        self.id = id
        self.x = x
        self.y = y
        self.orientation = orientation
        self.length = int(length)

    # Represents the vehicle object as a string
    def __repr__(self):
        return "'{0}{1}{2}{3}'".format(self.id, self.x, self.y, self.orientation)

    # Hash the vehicle with the representative string
    def __hash__(self):
        return hash(self.__repr__())

    # Compare two hashed vehicles
    def __eq__(self, other):
        return hash(self) == hash(other)