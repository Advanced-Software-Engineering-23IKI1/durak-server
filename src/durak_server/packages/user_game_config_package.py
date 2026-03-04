from __future__ import annotations
from durak_server.packages import BasePackage
from durak_server.config.game_config import GameConfig, BasicGameConfig
from durak_server.game.card import CardValue, Deck32, Deck52, Deck_creator
from typing import Union


class UserGameConfigPackage(BasePackage):
    PACKAGE_TYPE = "user-game-config"
    JSON_PARAM_MAP = {
        "card-order": "card_order",
        "attack-forwarding": "attack_forwarding",
        "player-card-count": "player_card_count",
        "dynamic-card-count-scaling": "dynamic_card_count_scaling",
        "all-card-defend-early-end": "all_card_defend_early_end",
    }

    def __init__(
        self,
        card_order: list[Union[CardValue, str]],
        attack_forwarding: dict[str, bool],
        player_card_count: int,
        dynamic_card_count_scaling: bool,
        all_card_defend_early_end: bool,
    ):
        """UserGameConfigPackage
        see the package documentation for more information

        Args:
            card_order (list[Union[CardValue, str]]): list of card values that dictates the order
            attack_forwarding (dict[str, bool]): attack forwarding ruleset
            player_card_count (int): amount of cards each player receives
            all_card_defend_early_end (bool): "Tu's Rule"

        Raises:
            ValueError: on invalid cards or attack_forwarding
        """

        if not self.is_card_order_valid(card_order=card_order):
            raise ValueError("card_order list is not valid")
        if not self.is_attack_forwarding_dict_valid(attack_forwarding):
            raise ValueError("attack_forwarding dict is not valid")
        self.__card_order = [CardValue(card) if isinstance(card, str) else card for card in card_order]
        self.__attack_forwarding = attack_forwarding
        self.__player_card_count = player_card_count
        self.__dynamic_card_count_scaling = dynamic_card_count_scaling
        self.__all_card_defend_early_end = all_card_defend_early_end

    def is_card_order_valid(self, card_order: list[Union[CardValue, str]]):
        """check if card_order list is valid
        This is performing only structural checks.
        More information on the required strcture and data can be found in the package documentation
        """
        return isinstance(card_order, list)

    def is_attack_forwarding_dict_valid(
        self, attack_forwarding: dict[str, bool]
    ) -> bool:
        """check if attack_forwarding dict is in the defined format
        This is performing only structural checks.
        More information on the required strcture and data can be found in the package documentation

        Args:
            attack_forwarding (dict[str, bool]): input dict

        Returns:
            bool: flag
        """
        keys = {"is-enabled", "exact-count-match"}
        return set(attack_forwarding.keys()) == keys

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "card-order": [value.value for value in self.__card_order],
            "attack-forwarding": self.__attack_forwarding,
            "player-card-count": self.__player_card_count,
            "dynamic-card-count-scaling": self.__dynamic_card_count_scaling,
            "all-card-defend-early-end": self.__all_card_defend_early_end,
        }
        return dict_repr

    @property
    def card_order(self) -> list[CardValue]:
        return self.__card_order

    @property
    def attack_forwarding(self) -> dict[str, bool]:
        return self.__attack_forwarding

    @property
    def player_card_count(self) -> int:
        return self.__player_card_count

    @property
    def dynamic_card_count_scaling(self) -> bool:
        return self.__dynamic_card_count_scaling

    @property
    def all_card_defend_early_end(self) -> bool:
        return self.__all_card_defend_early_end

    def __repr__(self):
        return f"UserGameConfigPackage({self.__card_order}, {self.attack_forwarding}, {self.player_card_count}, {self.all_card_defend_early_end})"

    @staticmethod
    def from_GameConfig(
        game_config: GameConfig, dynamic_card_count_scaling: bool
    ) -> UserGameConfigPackage:
        """generate a UserGameConfigPackage from a GameConfig object
        #! WARING: this method only uses
        Users are responsible for ensuring the game_config has a player_card_count set

        Args:
            game_config (GameConfig): the game config
            dynamic_card_count_scaling (bool): whether the card count scales dynamically

        Returns:
            UserGameConfigPackage: the package
        """
        card_order = list(
            dict.fromkeys([group[0].value for group in game_config.cards])
        )
        package = UserGameConfigPackage(
            card_order=card_order,
            attack_forwarding={
                "is-enabled": game_config.attack_forwarding,
                "exact-count-match": game_config.attack_forwarding_exact_count_match,
            },
            player_card_count=game_config.player_card_count,
            dynamic_card_count_scaling=dynamic_card_count_scaling,
            all_card_defend_early_end=game_config.all_card_defend_early_end,
        )
        return package

    def to_BasicGameConfig(self) -> BasicGameConfig:
        """generate a BasicGameConfig from the package

        Returns:
            BasicGameConfig: the resulting config object
        """
        # try to identify deck
        if frozenset(self.card_order) == frozenset(Deck32().values):
            deck = Deck32()
        elif frozenset(self.card_order) == frozenset(Deck52().values):
            deck = Deck52()
        else:
            deck = Deck_creator(self.card_order)

        return BasicGameConfig(
            attack_forwarding=self.attack_forwarding["is-enabled"],
            attack_forwarding_exact_count_match=self.attack_forwarding[
                "exact-count-match"
            ],
            all_card_defend_early_end=self.all_card_defend_early_end,
            card_order=self.card_order,
            deck=deck,
            player_card_count=self.player_card_count
        )
