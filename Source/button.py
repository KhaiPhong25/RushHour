import pygame

# Button class represents a clickable UI button with optional icon or text
class Button:
    def __init__(self, x, y, w, h, text = "", callback = None, font = None, icon_path = None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text                  # Optional text label
        self.callback = callback          # Function to call when clicked
        self.font = font                  # Font for text rendering
        self.base_icon = None             # Original icon image (if any)
        self.scaled_icon = None           # Resized version for hover effect
        self.hovered = False              # Whether the mouse is currently over the button
        self.scale_factor = 1.0           # Unused variable (could be removed)

        # Load and scale icon if provided
        if icon_path:
            icon = pygame.image.load(icon_path).convert_alpha()
            self.base_icon = pygame.transform.scale(icon, (w, h))
            self.scaled_icon = self.base_icon

    # Draw the button on the screen
    def draw(self, screen):
        if self.base_icon:
            # Scale up the icon when hovered (for hover effect)
            base_w, base_h = self.rect.width, self.rect.height
            scale = 1.2 if self.hovered else 1.0
            new_size = (int(base_w * scale), int(base_h * scale))
            self.scaled_icon = pygame.transform.scale(self.base_icon, new_size)

            # Center the scaled icon on the button rect
            icon_rect = self.scaled_icon.get_rect(center = self.rect.center)
            screen.blit(self.scaled_icon, icon_rect)

        elif self.text and self.font:
            # Render text if no icon is provided
            txt_surf = self.font.render(self.text, True, "#000000")
            txt_rect = txt_surf.get_rect(center = self.rect.center)
            screen.blit(txt_surf, txt_rect)

    # Handle mouse hover and click events
    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)  # Update hover state

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and self.callback:
                self.callback()  # Trigger callback if clicked

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

    # Update the button's icon dynamically
    def set_icon(self, icon_path):
        icon = pygame.image.load(icon_path).convert_alpha()
        self.base_icon = pygame.transform.scale(icon, (self.rect.width, self.rect.height))
        self.scaled_icon = self.base_icon
