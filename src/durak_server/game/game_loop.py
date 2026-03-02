from durak_server.config import GameConfig
from durak_server.player import Player

class GameLoop:
    def __init__(self, game_config: GameConfig, players: list[Player]):
        self.game_config = GameConfig
        self.players = players


    def game_start_routine(self):
        # game setup phase 2 in here (setting player order; distributing cards; communicating trump cards; drawpile)
        pass


    def loop(self):
        # game logic in here
        pass