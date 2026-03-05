import unittest

import os
import pathlib
import sys
import json

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from durak_server.config import BasicGameConfig, GameConfig
from durak_server.game.card import CardValue, Deck52, Deck32, CardDeck


DEFAULT_CARD_ORDER = [
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


class TestBasicConfig(unittest.TestCase):


    def get_all_values(self, config: GameConfig) -> list[CardValue]:
        """helper method to extract all values from a GameConfig
        #! expects classic trump/non-trump split. Does not work for 2-tier trump sytems
        """
        return list(dict.fromkeys([group[0].value for group in config.cards]))


    def test_001_card_generation_deck32_52(self):
        """test card generation on the BasicGameConfig using Deck32 and Deck52"""
        test_config_52 = BasicGameConfig(
            attack_forwarding=True,
            attack_forwarding_exact_count_match=False,
            all_card_defend_early_end=False,
            card_order=DEFAULT_CARD_ORDER,
            player_card_count = 7,
            deck = Deck52()
        )
        self.assertEqual(self.get_all_values(test_config_52), DEFAULT_CARD_ORDER)
        self.assertEqual(52, sum([len(group) for group in test_config_52.cards]))
        self.assertEqual(len(test_config_52.cards), len(DEFAULT_CARD_ORDER)*2)

        test_config_32 = BasicGameConfig(
            attack_forwarding=True,
            attack_forwarding_exact_count_match=False,
            all_card_defend_early_end=False,
            card_order=DEFAULT_CARD_ORDER,
            player_card_count = 7,
            deck = Deck32()
        )
        self.assertEqual(self.get_all_values(test_config_32), DEFAULT_CARD_ORDER[5:])
        self.assertEqual(32, sum([len(group) for group in test_config_32.cards]))
        self.assertEqual(len(test_config_32.cards), 16)


    def test_002_card_generation_order(self):
        """check if the card order provided is respected in the card generation"""
        my_order = [
            CardValue.THREE,
            CardValue.FOUR,
            CardValue.FIVE,
            CardValue.SIX,
            CardValue.SEVEN,
            CardValue.EIGHT,
            CardValue.NINE,
            CardValue.J,
            CardValue.TEN,
            CardValue.Q,
            CardValue.K,
            CardValue.A,
            CardValue.TWO,
        ]
        test_config = BasicGameConfig(
            attack_forwarding=True,
            attack_forwarding_exact_count_match=False,
            all_card_defend_early_end=False,
            card_order=my_order,
            player_card_count = 7,
            deck = Deck52()
        )
        self.assertEqual(self.get_all_values(test_config), my_order)


    def test_003_card_generation_trump_top(self):
        """check whether trump cards are grouped at the top according to the design"""

        test_config = BasicGameConfig(
            attack_forwarding=True,
            attack_forwarding_exact_count_match=False,
            all_card_defend_early_end=False,
            card_order=DEFAULT_CARD_ORDER,
            player_card_count = 7,
            deck = Deck52()
        )

        for group in test_config.cards[len(DEFAULT_CARD_ORDER):]:
            self.assertEqual(len(group), 1)
