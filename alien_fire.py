import pygame
from pygame.sprite import Sprite

class AlienFire(Sprite):
    """A class to mangage fire fired from the alien"""
    
    def __init__(self,ai_game):
        """Create a fire object at the alien's current position"""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.fire_color
        
        # Create a bullet rect at (0,0) and then set correct position
        self.rect = pygame.Rect(0,0, self.settings.fire_width,
                                self.settings.fire_height)
        self.rect.midbottom = ai_game.alien.rect.midbottom
        
        # Store the bullet's position as a decimal value.
        self.y = float(self.rect.y)
    
    def update(self):
        """Move the fire down the screen."""
        # update the decimal position of the bullet.
        self.y += self.settings.fire_speed
        #Update the rect position
        self.rect.y = self.y
    
    def draw_fire(self):
        """Draw the bullet to the screen"""
        pygame.draw.rect(self.screen, self.color, self.rect)