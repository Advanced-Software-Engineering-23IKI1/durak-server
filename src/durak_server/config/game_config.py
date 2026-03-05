from typing import Optional
from durak_server.game.card import Card, CardValue, CardDeck, CardSuit
from abc import ABC, abstractmethod
import random

class GameConfig(ABC):
    def __init__(
        self,
        attack_forwarding: bool,
        attack_forwarding_exact_count_match: bool,
        all_card_defend_early_end: int,
        player_card_count: Optional[int] = None,
    ):
        """Abstract Base Class for for game configuration

        Args:
            attack_forwarding (bool): flag for attack forwarding
            attack_forwarding_exact_count_match (bool): flag to toggle if exact attacking card count must be matched when forwarding (only applies when attack_forwarding=True)
            all_card_defend_early_end (int): flag for ending early if a player defends using his entire hand
            player_card_count (Optional[int]): amount of card each player receives. If set to None lobby decides depending on connected player count. Defaults to None
        """
        self.attack_forwarding = attack_forwarding
        self.attack_forwarding_exact_count_match = attack_forwarding_exact_count_match
        self.player_card_count = player_card_count
        self.all_card_defend_early_end = all_card_defend_early_end
        self._cards = self._generate_cards()

    @abstractmethod
    def _generate_cards(self) -> list[list[Card]]:
        pass

    @property
    def cards(self) -> list[list[Card]]:
        return self._cards


class BasicGameConfig(GameConfig):
    def __init__(
        self,
        attack_forwarding: bool,
        attack_forwarding_exact_count_match: bool,
        all_card_defend_early_end: bool,
        card_order: list[CardValue],
        deck: CardDeck,
        player_card_count: Optional[int] = None
    ):
        self.card_order = card_order
        self.deck = deck
        self.trump = None
        super().__init__(
            attack_forwarding=attack_forwarding,
            attack_forwarding_exact_count_match=attack_forwarding_exact_count_match,
            all_card_defend_early_end=all_card_defend_early_end,
            player_card_count=player_card_count,
        )

    def _generate_cards(self) -> list[list[Card]]:
        if self.trump is None:
            self._generate_trump()

        cards = self.deck.cards

        # card order validation
        values = list(set([card.value for card in cards]))
        if len(self.card_order) < len(values):
            raise ValueError("Card Order does not match Deck used")
        elif len(self.card_order) == len(values):
            if not set(self.card_order) == set(values):
                raise ValueError("Card Order does not match Deck used")
        else:
            if not set(values).issubset(set(self.card_order)):
                raise ValueError("Card Order does not match Deck used")

            self.card_order = [value for value in self.card_order if value in values]

        reg_cardgroups = {value: [] for value in self.card_order}
        trump_groups = {value: [] for value in self.card_order}

        for card in cards:
            if card.suit == self.trump:
                trump_groups[card.value].append(card)
            else:
                reg_cardgroups[card.value].append(card)

        cards = list(reg_cardgroups.values()) + list(trump_groups.values())
        return cards


    def _generate_trump(self):
        self.trump = random.choice(list({card.suit for card in self.deck.cards}))


