import sys
from time import sleep
import os
import pygame

from settings import Settings
from game_stats import GameStats, Mode
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien
from alien_fire import AlienFire as Fire

class AlienInvasion:
    """Overall class to manage game assets and behavior"""
    
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()
        
        # self.screen = pygame.display.set_mode((self.settings.screen_width, 
        #                                        self.settings.screen_height))
        self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")
        
                
        
        # Creat an instance to store game stats
        # and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.fire = pygame.sprite.Group()
        
        
        self._create_fleet()

        # Make the Play button.
        self.play_button = Button(self, "Play")
        
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            # Watch for keyboard and mouse events
            self._check_events()
            
            if self.stats.game_active:
                self.settings.reset_alien_speed()
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                
                self.fire.update()
                
            self._update_screen()   
            
          
    def _check_events(self):
        """Respond to keypresses and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)  
            
            
    def _check_play_button(self,mouse_pos):
        """Start a new game when the player clicks Play."""   
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)         
        # if self.play_button.rect.collidepoint(mouse_pos):
        if button_clicked and not self.stats.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()
            self._play_function()
        
    def _play_function(self):
        # Reset the game statistics 
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # Get rid of any remaining alien bullets
            self.aliens.empty()
            self.bullets.empty()
            self.fire.empty()
            
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            
            # Hide the mouse cursor
            pygame.mouse.set_visible(False)                
      
    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        # elif event.key == pygame.K_p:
        #     self.pause_game()
            
            # os.system('pause')

            
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
            if self.stats.game_active:
                self._fire_sound()
        elif event.key == pygame.K_s:
            self._play_function()
        elif event.type == pygame.K_f:
                self._alien_fire()  
        

    def pause_game(self):
        if self.stats.game_active:
            pygame.mixer.music.pause()
            self.stats.set_game_mode(Mode.PAUSE)
            os.system('pause')

        if self.stats.is_paused:
            pygame.mixer.music.unpause()
            self.stats.set_game_mode(Mode.ACTIVE)
            os.system('continue')

    # Fire Sound
    def _fire_sound(self):
        fire = pygame.mixer.Sound(os.path.join('sounds/fire.wav'))
        fire.set_volume(0.20)
        pygame.mixer.Sound.play(fire)
    
    # Collision sound
    def _hit_sound(self):
        hit = pygame.mixer.Sound(os.path.join('sounds/bangSmall.wav'))
        hit.set_volume(0.30)
        pygame.mixer.Sound.play(hit)
        
    
    def _check_keyup_events(self, event):
        """Respond to keypresses."""      
        if event.key == pygame.K_RIGHT:
                    self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
       
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullet's gruop"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
        
    def _alien_fire(self):
        """Create fire and add it to the alien fire group"""
        if len(self.fire) < self.settings.fire_allowed:
            
            new_fire = Fire(self)
            self.fire.add(new_fire)
            
        
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                 self.bullets.remove(bullet)  
                 
        self._check_bullet_alien_collisions()
    
    def _check_bullet_alien_collisions(self):
        # Check for any bullets that have hit aliens.
        # If so, get rid of the bullet and the alien. 
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
                self._hit_sound()
            self.sb.prep_score()
            self.sb.check_high_score()
            
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            
            # Increases level.
            self.stats.level += 1
            self.sb.prep_level()
      
    def _ship_hit(self):
        """Respond to the ship being hit by an alien"""
        
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()
            
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            
            # Pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
     
    def _update_fire(self):
        """Update position of bullets and get rid of old bullets."""
        # Update fire positions.
        self.fire.update()

        # Get rid of bullets that have disappeared.
        
                 
        for fire in self.fire.copy():
            if fire.rect.bottom <= 0:
                 self.fire.remove(fire)
        
    def _check_aliens_bottom(self):
        """Chbeck if any aliens have reachced the bottom of the screen."""
        
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat the same as if the ship got hit.
                self._ship_hit()
                break
                 
    def _create_fleet(self):
        """Creat the fleet of alins"""
        # Make an alien
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height -
                            (3 *  alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
       
    def _create_alien(self,alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
        
    
    def _alien_sound(self):
        alien_sound = pygame.mixer.Sound(os.path.join('sounds/beat1.wav'))
        alien_sound.play(1)
        
    
    
    def _update_aliens(self):
        """
        Check if the fleet is at an edge, then update 
            the positions of all aliens in the fleet
        """
        self._check_fleet_edges()
        
        self.aliens.update()
        
        
        
        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            #print("Ship hit!!!")
            
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
        
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._alien_sound()
                self._change_fleet_direction()
                
                break
            
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        
        
    
    
    def _update_screen(self):
        # Redraw the screen during each pass through the loop
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        
        for fire in self.fire.sprites():
            fire.draw_fire()
        
        self.aliens.draw(self.screen)
        
        
        # Draw the score information
        self.sb.show_score()
        
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
        
        # Make the most recently drawn screen visible
        pygame.display.flip()
                
if __name__ =='__main__':
    # Make a game instance, and run the game
    ai = AlienInvasion()
    ai.run_game()