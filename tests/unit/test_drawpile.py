import unittest

import os
import pathlib
import sys
import json


here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from durak_server.game.drawpile import DrawPile
from durak_server.game.card import Deck32, CardSuit

class TestDrawPile(unittest.TestCase):
    
    def test_001_drawpile_init(self):
        """test if drawpile initializes correctly with given cards"""
        test_cards = Deck32().cards
        drawpile = DrawPile(test_cards, CardSuit.HEARTS)
        self.assertEqual(len(drawpile._cards), len(test_cards), f"{len(drawpile._cards)} cards in drawpile, expected {len(test_cards)}")

    def test_002_drawpile_draw(self):
        """test if drawpile draws the correct amount of cards and removes them from the drawpile"""
        test_cards = Deck32().cards
        drawpile = DrawPile(test_cards, CardSuit.HEARTS)
        drawn_cards = drawpile.draw(6)
        self.assertEqual(len(drawn_cards), 6, f"{len(drawn_cards)} cards drawn, expected 6")
        self.assertEqual(len(drawpile._cards), len(test_cards) - 6, f"{len(drawpile._cards)} cards left in drawpile, expected {len(test_cards) - 6}")

    def test_003_drawpile_draw_too_many(self):
        """test if drawpile draws all remaining cards if requested count exceeds the amount of cards in the drawpile"""
        test_cards = Deck32().cards
        drawpile = DrawPile(test_cards, CardSuit.HEARTS)
        drawn_cards = drawpile.draw(len(test_cards) + 5)
        self.assertEqual(len(drawn_cards), len(test_cards), f"{len(drawn_cards)} cards drawn, expected {len(test_cards)}")
        self.assertEqual(len(drawpile._cards), 0, f"{len(drawpile._cards)} cards left in drawpile, expected 0")

    def test_004_drawpile_draw_trump(self):
        """test if drawpile draws the correct trump card"""
        test_cards = Deck32().cards
        drawpile = DrawPile(test_cards, CardSuit.HEARTS)
        trump_card = drawpile.trump_card
        self.assertIsNotNone(trump_card, "Expected trump card not found")
        self.assertEqual(trump_card.suit, CardSuit.HEARTS, f"Expected trump card of suit {CardSuit.HEARTS}, got {trump_card.suit}")

    def test_005_drawpile_depletion_draws_trump_last(self):
        """test if drawpile depletes correctly and the trump card is drawn last"""
        test_cards = Deck32().cards
        drawpile = DrawPile(test_cards, CardSuit.HEARTS)

        trump_card = drawpile.trump_card
        drawn_without_trump = drawpile.draw(len(drawpile))

        self.assertEqual(len(drawpile), 0, "Expected draw pile to be empty excluding trump card")
        self.assertEqual(len(drawpile._cards), 1, "Expected only the trump card to remain in internal storage")
        self.assertNotIn(trump_card, drawn_without_trump, "Trump card must not be drawn before draw pile depletion")

        drawn_trump = drawpile.draw(1)
        self.assertEqual(drawn_trump, [trump_card], "Expected trump card to be drawn last")

        self.assertEqual(drawpile.draw(1), [], "Expected no cards to be drawn after full depletion")
        self.assertEqual(len(drawpile._cards), 0, "Expected internal storage to be empty after drawing trump")

if __name__ == "__main__":
    unittest.main()