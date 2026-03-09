from durak_server.config import GameConfig
from durak_server.player import Player
from durak_server.game.drawpile import DrawPile
from random import shuffle

import durak_server.packages
from durak_server.player import PlayerGameStatus

class GameLoop:
    def __init__(self, game_config: GameConfig, players: list[Player]):
        self._game_config = game_config
        shuffle(players) # this is theoretically part of the game start routine but the players structure is optimally a immutable tuple
        self._players = tuple(players) 
        self.game_start_routine()

    def broadcast(self, package):
        for player in self._players:
            player.send_package(package)
            
   
    def broadcast_player_hands_update(self):
        for player in self.players:
            player.send_package(durak_server.packages.PlayerHandsUpdatePackage(
                hand=player.hand,
                player_hands=[{"player_id": other_player.id, "card_count": len(other_player.hand)} for other_player in self.players if other_player != player],
                draw_pile=len(self._drawpile),
                trump=self._trump_card.id if self._trump_card else None,
                player_order=[p.id for p in self._players]
            ))

    def game_start_routine(self):
        self._drawpile = DrawPile(self._game_config.cards)
        self._trump_suit = self._game_config.trump
        self._trump_card = self._drawpile.draw_trump(self._trump_suit)
        
        # distributing cards to players
        for player in self._players:
            player.hand = self._drawpile.draw(self._game_config.player_card_count)
        self.broadcast_player_hands_update()    
        
        # set player stati
        self._players[0].game_status = PlayerGameStatus.Attacker
        self.broadcast(durak_server.packages.PlayerStatusPackage(
            statuses=[{
                "player_id": player.id,
                "status": player.game_status
            } for player in self._players]
        ))
        
        
        
        
        
        
        

        # game setup phase 2 in here (setting player order; distributing cards; communicating trump cards; drawpile)
        pass


    def loop(self):
        # game logic in here
        pass
    