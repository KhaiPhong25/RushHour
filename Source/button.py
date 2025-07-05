import pygame
import colors

class Button:
    def __init__(self, x, y, w, h, text, callback, font, icon_path):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.font = font
        self.icon = None

        if icon_path:
            self.icon = pygame.image.load(icon_path).convert_alpha()
            self.icon = pygame.transform.scale(self.icon, (w, h))

    def draw(self, screen):
        #pygame.draw.rect(screen, colors.SKY_BLUE, self.rect, border_radius = 10) # button background
        #pygame.draw.rect(screen, colors.DARK_GRAY, self.rect, width = 5, border_radius = 10)    # button frame

        if self.icon:
            icon_rect = self.icon.get_rect(center = self.rect.center)
            screen.blit(self.icon, icon_rect)
            
        elif self.text and self.font:
            txt_surf = self.font.render(self.text, True, colors.BLACK)
            txt_rect = txt_surf.get_rect(center = self.rect.center)
            screen.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def set_icon(self, icon_path):
        icon = pygame.image.load(icon_path).convert_alpha()
        icon = pygame.transform.scale(icon, (self.rect.width - 10, self.rect.height - 10))
        self.icon = icon
