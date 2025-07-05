import pygame
from gameboard import Gameboard
from vehicleSprite import VehicleSprite

class BoardRenderer:
    def __init__(self, gameboard: Gameboard, board_image_path, cell_size = 62, grid_size = 6, offset_x = 275, offset_y = 172):
        self.gameboard = gameboard
        self.cell_size = cell_size
        self.grid_size = grid_size
        
        # Load the board image and scale it to fit the window size
        self.board_image = pygame.image.load(board_image_path).convert()
        original_width, original_height = self.board_image.get_size()
        self.board_image = pygame.transform.scale(self.board_image, (800, 650))

        scale_x = 800 / original_width
        scale_y = 650 / original_height
        self.offset_x = int(offset_x * scale_x)
        self.offset_y = int(offset_y * scale_y)

        self.vehicle_sprites = []
        for vehicle in self.gameboard.vehicles:
            image_path = f"Images/Vehicles/{vehicle.id}{vehicle.orientation}{vehicle.length}.png"
            self.vehicle_sprites.append(VehicleSprite(vehicle, image_path, self.cell_size))

    def draw(self, screen):
        screen.blit(self.board_image, (0, 0))  # Draw the board image at the top-left corner
        for sprite in self.vehicle_sprites:
            sprite.draw(screen, self.cell_size, self.offset_x, self.offset_y)

    def update(self, gameboard: Gameboard):
        self.gameboard = gameboard
        
        # Create a dictionary to map vehicle IDs to their sprites
        sprite_dict = {sprite.vehicle.id: sprite for sprite in self.vehicle_sprites}
        new_vehicle_sprites = []
        
        for vehicle in gameboard.vehicles:
            if vehicle.id in sprite_dict:
                sprite = sprite_dict[vehicle.id]
                sprite.update(vehicle)
                new_vehicle_sprites.append(sprite)
            else:
                image_path = f"Image/Vehicles/{vehicle.id}{vehicle.orientation}{vehicle.length}.png"
                new_vehicle_sprites.append(VehicleSprite(vehicle, image_path, self.cell_size))
        
        self.vehicle_sprites = new_vehicle_sprites
