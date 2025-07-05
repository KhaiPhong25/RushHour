import pygame
from vehicle import Vehicle

# VehicleSprite handles rendering a vehicle image on the screen based on its state
class VehicleSprite:
    def __init__(self, vehicle: Vehicle, image_path, cell_size):
        self.vehicle = vehicle  
        self.image = pygame.image.load(image_path).convert_alpha()

        # Determine image size based on vehicle orientation and length
        if vehicle.orientation == 'H':  # Horizontal vehicle
            width = cell_size * vehicle.length
            height = cell_size
        else:  # Vertical vehicle
            width = cell_size
            height = cell_size * vehicle.length

        # Resize the image to fit the appropriate grid cell size
        self.image = pygame.transform.scale(self.image, (width, height))

    # Draw the vehicle on the screen at its current grid position
    def draw(self, screen, cell_size, offset_x, offset_y):
        x = self.vehicle.x * cell_size + offset_x  # Convert grid X to pixel X
        y = self.vehicle.y * cell_size + offset_y  # Convert grid Y to pixel Y
        
        screen.blit(self.image, (x, y))  # Draw the vehicle image at computed position

    # Update the internal position based on a new Vehicle object (used during animation)
    def update(self, vehicle: Vehicle):
        self.vehicle.x = vehicle.x
        self.vehicle.y = vehicle.y
