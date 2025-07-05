import pygame
from vehicle import Vehicle

class VehicleSprite:
    def __init__(self, vehicle: Vehicle, image_path, cell_size):
        self.vehicle = vehicle
        self.image = pygame.image.load(image_path).convert_alpha()

        if vehicle.orientation == 'H':
            width = cell_size * vehicle.length
            height =  cell_size
        else:
            width = cell_size
            height = cell_size * vehicle.length
        
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, screen, cell_size, offset_x, offset_y):
        x = self.vehicle.x * cell_size + offset_x
        y = self.vehicle.y * cell_size + offset_y
        
        screen.blit(self.image, (x, y))

    def update(self, vehicle: Vehicle):
        self.vehicle.x = vehicle.x
        self.vehicle.y = vehicle.y