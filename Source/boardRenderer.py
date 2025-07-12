import pygame
import config
from gameboard import Gameboard        
from vehicleSprite import VehicleSprite  
from path import resource_path

# BoardRenderer handles rendering the game board and vehicles on screen
class BoardRenderer:
    def __init__(self, gameboard: Gameboard, board_image_path, cell_size = 62, grid_size = 6, offset_x = 275, offset_y = 172):
        self.gameboard = gameboard      # The game logic board
        self.cell_size = cell_size      # Size of each grid cell in pixels
        self.grid_size = grid_size      # Number of rows/columns (default is 6 for Rush Hour)

        # Load and scale the board background image to match the screen size
        self.board_image = pygame.image.load(board_image_path).convert()
        original_width, original_height = self.board_image.get_size()
        self.board_image = pygame.transform.scale(self.board_image, (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))

        # Calculate scaled offset to correctly align vehicles on resized board
        scale_x = config.SCREEN_WIDTH / original_width
        scale_y = config.SCREEN_HEIGHT / original_height
        self.offset_x = int(offset_x * scale_x)
        self.offset_y = int(offset_y * scale_y)

        # Create a list of VehicleSprite objects from the initial gameboard state
        self.vehicle_sprites = []
        for vehicle in self.gameboard.vehicles:
            image_path = resource_path(f"Images/Vehicles/{vehicle.id}{vehicle.orientation}{vehicle.length}.png")
            self.vehicle_sprites.append(VehicleSprite(vehicle, image_path, self.cell_size))

    # Draw the board and all vehicle sprites on the screen
    def draw(self, screen):
        screen.blit(self.board_image, (0, 0))  # Draw the game board background at (0,0)
        for sprite in self.vehicle_sprites:
            sprite.draw(screen, self.cell_size, self.offset_x, self.offset_y)  # Draw each vehicle sprite

    # Update the board renderer with a new gameboard state
    def update(self, gameboard: Gameboard):
        self.gameboard = gameboard

        # Create a lookup dictionary of current sprites by vehicle ID
        sprite_dict = {sprite.vehicle.id: sprite for sprite in self.vehicle_sprites}
        new_vehicle_sprites = []

        for vehicle in gameboard.vehicles:
            if vehicle.id in sprite_dict:
                # If vehicle already exists, update its position
                sprite = sprite_dict[vehicle.id]
                sprite.update(vehicle)
                new_vehicle_sprites.append(sprite)

            else:
                # If new vehicle, create new sprite
                image_path = resource_path(f"Images/Vehicles/{vehicle.id}{vehicle.orientation}{vehicle.length}.png")
                new_vehicle_sprites.append(VehicleSprite(vehicle, image_path, self.cell_size))

        # Replace the current sprite list with the updated one
        self.vehicle_sprites = new_vehicle_sprites
    
    def update_main_vehicle_final_animation(self, gameboard, final_move):
        # Create a lookup dictionary of current sprites by vehicle ID
        sprite_dict = {sprite.vehicle.id: sprite for sprite in self.vehicle_sprites}
        new_vehicle_sprites = []

        for vehicle in gameboard.vehicles:
            if vehicle.id in sprite_dict:
                sprite = sprite_dict[vehicle.id]

                if vehicle.id == "#":
                    sprite.update_x_to_move(final_move)
                    
                # If vehicle already exists, update its position
                sprite = sprite_dict[vehicle.id]
                new_vehicle_sprites.append(sprite)

        # Replace the current sprite list with the updated one
        self.vehicle_sprites = new_vehicle_sprites