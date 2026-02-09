from abc import ABC, abstractmethod
from durak_server import Player
import datetime

class EndCondition(ABC):

    @abstractmethod
    def is_game_end(self) -> bool:
        pass


class EndConditionFactory(ABC):

    @abstractmethod
    def create_EndCondition(self, **kwargs) -> EndCondition:
        """create the EndConditionObject"""
        pass