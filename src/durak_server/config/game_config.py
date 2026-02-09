from typing import Optional
from durak_server.config.end_condition import EndConditionFactory

class GameConfig:
    def __init__(
        self,
        end_condition_factory: EndConditionFactory, 
        base_scoreboard_top_players = 5):
        self.endcondition_factory = end_condition_factory
        self.base_scoreboard_top_players = base_scoreboard_top_players



class GameConfigFactory:
    def __init__(
        self,
        end_condition_factory: EndConditionFactory, 
        base_scoreboard_top_players = 5):
        self.__base_scoreboard_top_players = base_scoreboard_top_players
        self.__base_endcondition = end_condition_factory

    def create_game_config(self) -> GameConfig:
        """Creates a new GameConfig object using the config provided to the factory

        Returns:
            GameConfig: A new GameConfig object
        """
        return GameConfig(
            end_condition_factory = self.__base_endcondition,
            base_scoreboard_top_players=self.__base_scoreboard_top_players)
