import unittest

import os
import pathlib
import sys
import json

from durak_server.game.card import Deck52

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from durak_server.config import BasicGameConfig, GameConfig
from durak_server.game.game_loop import GameLoop


class TestGameLoop(unittest.TestCase):

    def test_001_game_start_routine(self):
        """test if game start routine runs without error and sets up the game state correctly (cards in this case)"""
        test_config = BasicGameConfig(
            attack_forwarding=True,
            attack_forwarding_exact_count_match=False,
            all_card_defend_early_end=False,
            card_order=[],
            deck=Deck52(),
        )
        game_loop = GameLoop(game_config=test_config, players=[])
        game_loop.game_start_routine()
        self.assertEqual(game_loop.cards, test_config.cards)
