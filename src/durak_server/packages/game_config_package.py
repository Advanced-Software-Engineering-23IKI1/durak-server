from __future__ import annotations
from durak_server.packages import BasePackage
from durak_server.config.game_config import GameConfig, BasicGameConfig
from durak_server.game.card import CardValue, Deck32, Deck52, Deck_creator
from typing import Union


class GameConfigPackage(BasePackage):
    PACKAGE_TYPE = "game-config"
    JSON_PARAM_MAP = {
        "cards": "cards",
        "attack-forwarding": "attack_forwarding",
        "player-card-count": "player_card_count",
        "dynamic-card-count-scaling": "dynamic_card_count_scaling",
        "all-card-defend-early-end": "all_card_defend_early_end",
    }

    def __init__(
        self,
        cards: list[list[dict[str, Union[str, int]]]],
        attack_forwarding: dict[str, bool],
        player_card_count: int,
        dynamic_card_count_scaling: bool,
        all_card_defend_early_end: bool,
    ):
        """GameConfigPackage
        see the package documentation for more information

        Args:
            cards (list[list[dict[str, Union[str, int]]]]): list of equivalent card strength groups. Each card described by a dict according to package-design
            attack_forwarding (dict[str, bool]): attack forwarding ruleset
            player_card_count (int): amount of cards each player receives
            all_card_defend_early_end (bool): "Tu's Rule"

        Raises:
            ValueError: on invalid cards or attack_forwarding
        """

        if not self.is_cards_list_valid(cards):
            raise ValueError("cards list is not valid")
        if not self.is_attack_forwarding_dict_valid(attack_forwarding):
            raise ValueError("attack_forwarding dict is not valid")
        self.__cards = cards
        self.__attack_forwarding = attack_forwarding
        self.__player_card_count = player_card_count
        self.__dynamic_card_count_scaling = dynamic_card_count_scaling
        self.__all_card_defend_early_end = all_card_defend_early_end

    def is_cards_list_valid(
        self, cards: list[list[dict[str, Union[str, int]]]]
    ) -> bool:
        """check if cards list is in the defined format
        This is performing only structural checks.
        More information on the required structure and data can be found in the package documentation

        Args:
            cards (list[list[dict[str, Union[str, int]]]]): input list

        Returns:
            bool: flag
        """
        keys = {"value", "suit", "id"}
        try:
            for cardgroup in cards:
                for card in cardgroup:
                    if not set(card.keys()) == keys:
                        return False
            return True
        except (KeyError, TypeError, AttributeError):
            return False

    def is_attack_forwarding_dict_valid(
        self, attack_forwarding: dict[str, bool]
    ) -> bool:
        """check if attack_forwarding dict is in the defined format
        This is performing only structural checks.
        More information on the required structure and data can be found in the package documentation

        Args:
            attack_forwarding (dict[str, bool]): input dict

        Returns:
            bool: flag
        """
        keys = {"is-enabled", "exact-count-match"}
        return set(attack_forwarding.keys()) == keys

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "cards": self.__cards,
            "attack-forwarding": self.__attack_forwarding,
            "player-card-count": self.__player_card_count,
            "dynamic-card-count-scaling": self.__dynamic_card_count_scaling,
            "all-card-defend-early-end": self.__all_card_defend_early_end
        }
        return dict_repr

    @property
    def cards(self) -> list[list[dict[str, Union[str, int]]]]:
        return self.__cards

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
        return f"GameConfigPackage({self.cards}, {self.attack_forwarding}, {self.player_card_count}, {self.all_card_defend_early_end})"

    @staticmethod
    def from_GameConfig(game_config: GameConfig, dynamic_card_count_scaling: bool) -> GameConfigPackage:
        """generate a GameConfigPackage from a GameConfig object
        #! WARING: this method performs no data checks.
        Users are responsible for ensuring the game_config has a player_card_count set

        Args:
            game_config (GameConfig): the game config

        Returns:
            GameConfigPackage: the package
        """
        return GameConfigPackage(
            cards=[
                [vars(card) for card in cardgroups]
                for cardgroups in game_config.cards
            ],
            attack_forwarding={
                "is-enabled": game_config.attack_forwarding,
                "exact-count-match": game_config.attack_forwarding_exact_count_match,
            },
            player_card_count=game_config.player_card_count,
            dynamic_card_count_scaling=dynamic_card_count_scaling,
            all_card_defend_early_end=game_config.all_card_defend_early_end,
        )
    
    def to_BasicGameConfig(self) -> BasicGameConfig | None:
        """try to generate a BasicGameConfig from the package
        #! WARNING: this method is considered UNSTABLE and should only be used if confident
        #! that the package can be parsed to a BasicGameConfig. Checks do not cover all edge cases !

        Returns:
            BasicGameConfig | None: the resulting config object or None if generation is not possible
        """
        try:
            card_value_order = []
            for cardgroup in self.cards:
                if cardgroup[0]["value"] not in card_value_order:
                    card_value_order.append(cardgroup[0]["value"])
            if frozenset(card_value_order) == frozenset(Deck32().values):
                deck = Deck32()
            elif frozenset(card_value_order) == frozenset(Deck52().values):
                deck = Deck52()
            else:
                deck = Deck_creator(card_value_order)
            return BasicGameConfig(
                attack_forwarding=self.attack_forwarding["is-enabled"],
                attack_forwarding_exact_count_match=self.attack_forwarding["exact-count-match"],
                all_card_defend_early_end=self.all_card_defend_early_end,
                card_order=card_value_order,
                deck=deck,
                player_card_count=self.player_card_count
            )
        except Exception as e:
            return None
