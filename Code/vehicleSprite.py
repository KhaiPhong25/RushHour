import pygame
import math
from Code.vehicle import Vehicle

# VehicleSprite handles rendering a vehicle image on the screen based on its state
class VehicleSprite:

    # Constructor of VehicleSprite class
    def __init__(self, vehicle: Vehicle, image_path, cell_size):
        self.vehicle = vehicle  # Vehicle object representing position and orientation
        self.image = pygame.image.load(image_path).convert_alpha()  # Load vehicle image with transparency

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
        # Convert grid coordinates to screen pixel coordinates
        x = self.vehicle.x * cell_size + offset_x
        y = self.vehicle.y * cell_size + offset_y
        
        # Draw the vehicle image at computed position
        screen.blit(self.image, (x, y))

        # Draw an outline around the vehicle if it is the main vehicle
        if self.vehicle.id == "#":
            # Pulse effect for the outline color using sine wave and current time
            pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.005))
            outline_color = (255, 255, pulse)

            # Create a rectangle for the outline, slightly larger than the vehicle image
            rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

            # Draw the glowing outline rectangle
            pygame.draw.rect(screen, outline_color, rect.inflate(8, 8), 3)

    # Update the internal position based on a new Vehicle object (used during animation)
    def update(self, vehicle: Vehicle):
        self.vehicle.x = vehicle.x
        self.vehicle.y = vehicle.y

    # Manually update only the X position by a delta (used for animation or effects)
    def update_x_to_move(self, move):
        self.vehicle.x += move
