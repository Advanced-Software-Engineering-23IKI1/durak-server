from durak_server.game.card import Card, CardSuit

from collections import deque
from random import shuffle


class DrawPile:
    def __init__(self, cards: list[Card], trump_suit: CardSuit):
        """A class representing the draw pile in a game of Durak. It is initialized with a list of cards and a trump suit. 
        The draw pile is shuffled upon initialization and the trump card is drawn and set on the bottom of the pile. It does not count towards the length of the draw pile.

        Args:
            cards (list[Card]): cards to initialize the draw pile with.
            trump_suit (CardSuit): _description_
        """
        shuffle(cards)  # this is inplace
        self._cards = deque(cards)
        self._trump_card = self._draw_trump(trump_suit)

    @property
    def trump_card(self) -> Card:
        return self._trump_card

    def draw(self, count: int) -> list[Card]:
        """Draw cards from the draw pile

        Args:
            count (int): amount of cards to draw
        Returns:
            list[Card]: drawn cards. If number of requested cards exceeds the amount of cards in the draw pile, all remaining cards will be drawn and returned
        """

        if len(self._cards) == 0 or count <= 0:
            return []
        if len(self._cards) < count:
            return self.draw(len(self._cards))

        drawn_cards = []
        for _ in range(count):
            if self._cards:
                drawn_cards.append(self._cards.popleft())
            else:
                break
        return drawn_cards

    def _draw_trump(self, suit: CardSuit) -> Card:
        """Draws first card from the pile with matching suit and sets it as trump card. If no card with the given suit is found, None is returned and no card is set as trump card.

        Args:
            suit (CardSuit): The suit of the trump card to draw

        Returns:
            Card: The drawn trump card
        """

        for card in self._cards:
            if card.suit == suit:
                self._cards.remove(card)
                self._cards.append(card)  # put the trump card at the bottom of the pile
                self._trump_card = card
                return self._trump_card
        return None

    def __len__(self):
        if len(self._cards) == 0:
            return 0
        return len(self._cards) - 1  # the trump card is not part of the draw pile, it is drawn at the start of the game and placed aside
