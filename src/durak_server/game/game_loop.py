from durak_server.config import GameConfig
from durak_server.player import Player
from durak_server.game.drawpile import DrawPile
from random import shuffle

import durak_server.packages
from durak_server.player import PlayerGameStatus

class GameLoop:
    def __init__(self, game_config: GameConfig, players: list[Player], logger: SessionLogger):
        self._game_config = game_config
        shuffle(players) # this is theoretically part of the game start routine but the players structure is optimally a immutable tuple
        self._players = tuple(players) 
        self._logger = logger
        self._game_player_list = self._players().copy(deep=False)  # list of players still in game
        self._leaderboard = []
        self._attack_buffer = {}  # mapping dict for the current attack
        self._attack_max = 0  # max amount of cards valid for attacking (=initial defender hand count)
        self._attacker_list = []
        self._cur_attacker_idx = 0
        self.game_start_routine()

    @property
    def players(self) -> tuple[Player, ...]:
        return self._players

    def broadcast(self, package):
        for player in self._players:
            player.send_package(package)
            
   
    def broadcast_player_hands_update(self):
        for player in self.players:
            player.send_package(durak_server.packages.PlayerHandsUpdatePackage(
                hand=[card.id for card in player.hand],
                player_hands=[{"player_id": other_player.player_id, "card_count": len(other_player.hand)} for other_player in self.players if other_player != player],
                draw_pile=len(self._drawpile),
                trump=self._trump_card.id if self._trump_card else None,
                player_order=[p.player_id for p in self._players]
            ))

    def game_start_routine(self):
        self._trump_suit = self._game_config.trump
        deck_cards = [card for card_group in self._game_config.cards for card in card_group]
        self._drawpile = DrawPile(deck_cards, self._trump_suit)
        self._trump_card = self._drawpile.trump_card
        
        # distributing cards to players
        for player in self._players:
            player.hand = self._drawpile.draw(self._game_config.player_card_count)
        self.broadcast_player_hands_update()    
        
        # set player stati
        self._players[0].game_status = PlayerGameStatus.Attacker
        self.broadcast(durak_server.packages.PlayerStatusPackage(
            statuses=[{
                "player_id": player.player_id,
                "status": player.game_status
            } for player in self._players]
        ))
        
        
        
        
        
        
        

        # game setup phase 2 in here (setting player order; distributing cards; communicating trump cards; drawpile)
        pass


    def loop(self):
        # game logic in here
        pass
    