from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

class CardSuit(str, Enum):
    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    HEARTS = "hearts"
    SPADES = "spades"


class CardValue(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"

    J = "J"
    Q = "Q"
    K = "K"
    A = "A"

    _2 = TWO
    _3 = THREE
    _4 = FOUR
    _5 = FIVE
    _6 = SIX
    _7 = SEVEN
    _8 = EIGHT
    _9 = NINE
    _10 = TEN


@dataclass(frozen=True)
class Card:
    """class representing a Card"""
    id: int
    suit: CardSuit
    value: CardValue


class CardDeck(ABC):
    def __init__(self):
        self._cards = self._build_deck()

    @property
    def cards(self) -> list[Card]:
        return self._cards

    def _build_deck(self) -> list[Card]:
        cards = []
        card_id = 1

        for suit in CardSuit:
            for value in self.values():
                cards.append(Card(id=card_id, suit=suit, value=value))
                card_id += 1

        return cards

    @abstractmethod
    def values(self) -> list[CardValue]:
        """Return the card values used to generate the deck cards"""
        pass

    def __hash__(self):
        return len(self.cards)


class Deck52(CardDeck):
    def values(self) -> list[CardValue]:
        return [
            CardValue.TWO,
            CardValue.THREE,
            CardValue.FOUR,
            CardValue.FIVE,
            CardValue.SIX,
            CardValue.SEVEN,
            CardValue.EIGHT,
            CardValue.NINE,
            CardValue.TEN,
            CardValue.J,
            CardValue.Q,
            CardValue.K,
            CardValue.A,
        ]
    


class Deck32(CardDeck):
    def values(self) -> list[CardValue]:
        return [
            CardValue.SEVEN,
            CardValue.EIGHT,
            CardValue.NINE,
            CardValue.TEN,
            CardValue.J,
            CardValue.Q,
            CardValue.K,
            CardValue.A,
        ]
