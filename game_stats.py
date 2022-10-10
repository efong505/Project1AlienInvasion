from enum import Enum

class Mode(Enum):
    ACTIVE = (1,)
    NOT_ACTIVE = (2,)
    CHANGING_LEVEL = 3
    LEVEL_CHANGED = 4
    KILLED = 5
    GAME_OVER = 6
    MENU = 7
    PAUSE = 8

class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        
        # Start Alien Invasion in an inactive state.
        self.game_active = False
        
        # High score should never be reset
        self.high_score = 0

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def set_game_mode(self, mode: Mode):
        self.game_mode = mode
    
    @property
    def is_paused(self) -> bool:
        return self.game_mode == Mode.PAUSE

    @property
    def is_active(self) -> bool:
        return self.game_mode == Mode.ACTIVE