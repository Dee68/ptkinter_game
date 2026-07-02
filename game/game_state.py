# the game state object and it's properties goes here
from enum import Enum, auto

class GameState(Enum):
    """
     Shows possible state of the game
    """
    INTRO = auto()
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    
    