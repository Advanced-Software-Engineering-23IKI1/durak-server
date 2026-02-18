from durak_server.packages import BasePackage
from typing import Optional


class PlayerHandsUpdatePackage(BasePackage):
    PACKAGE_TYPE = "player-hands-update"
    JSON_PARAM_MAP = {
        "hand": "hand",
        "player-hands": "player_hands",
        "draw-pile": "draw_pile",
        "trump": "trump",
        "player-order": "player_order",
    }

    def __init__(
        self,
        hand: list[int],
        player_hands: list[dict[str, Optional[int]]],
        draw_pile: int,
        trump: Optional[int],
        player_order: list[int],
    ):
        """PlayerHandsUpdatePackage
        see the package documentation for more information

        Args:
            hand (list[int]): array of card ids the player is holding
            player_hands (list[dict[str, int]]): list of card counts in other players' hands
            draw_pile (int): amount of cards on the draw pile (excluding additional trump card)
            trump (int): card id of the trump card (null if the card has been drawn)
            player_order (list[int]): array of player id's in playing order

        Raises:
            ValueError: on invalid player list
        """
        self.__hand = hand
        if not self.is_player_hands_list_valid(player_hands):
            raise ValueError("player hands list is not valid")
        self.__player_hands = player_hands
        self.__draw_pile = draw_pile
        self.__trump = trump
        self.__player_order = player_order

    def is_player_hands_list_valid(self, player_hands: list[dict]) -> bool:
        """check if player hands list is in the defined format
        This is performing only structural checks.
        More information on the required strcture and data can be found in the package documentation

        Args:
            player_hands (list[dict]): input player_hands

        Returns:
            bool: flag
        """
        keys = {"player_id", "card_count"}
        return all(set(player.keys()) == keys for player in player_hands)

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "hand": self.__hand,
            "player-hands": self.__player_hands,
            "draw-pile": self.__draw_pile,
            "trump": self.__trump,
            "player-order": self.__player_order
        }
        return dict_repr
    
    @property
    def hand(self) -> list[int]:
        return self.__hand
    
    @property
    def player_hands(self) -> list[dict[str, Optional[int]]]:
        return self.__player_hands
    
    @property
    def draw_pile(self) -> int:
        return self.__draw_pile
    
    @property
    def trump(self) -> Optional[int]:
        return self.__trump
    
    @property
    def player_order(self) -> list[int]:
        return self.__player_order

    def __repr__(self):
        return f"PlayerHandsUpdatePackage({self.hand}, {self.player_hands}, {self.draw_pile}, {self.trump}, {self.player_order})"
