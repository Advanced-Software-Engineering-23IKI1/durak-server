from durak_server.config.game_config import GameConfigFactory, GameConfig




# temporary end conditions
from durak_server.config.end_condition import EndCondition, EndConditionFactory


class TemporaryEndCondition(EndCondition):

    def is_game_end(self):
        return False
    
class TemporaryEndConditionFactory(EndConditionFactory):

    def create_EndCondition(self, **kwargs):
        return TemporaryEndCondition

default_game_config_factory = GameConfigFactory(
    end_condition_factory=TemporaryEndConditionFactory
)
