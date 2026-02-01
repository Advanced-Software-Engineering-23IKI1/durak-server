import unittest

import os
import pathlib
import sys

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from bbc_server.packages import *


class PackageTest(unittest.TestCase):
    """class for testing packages (mainly input validation on nested structures)"""

    def test_001_EndRoutinePackage_scoreboard_validation(self):
        """test validation of scoreboard on EndRoutinePackage"""
        self.assertRaises(ValueError, EndRoutinePackage, score=10, is_winner=True, scoreboard=[{}])  # empty dict
        # missing attributes on second dict
        self.assertRaises(ValueError, EndRoutinePackage, score=10, is_winner=True, scoreboard=[{"playername": "player1", "score": 10}, {}])

    def test_002_GameUpdatePackage_playerlist_validation(self):
        """test validation of top-players on GameUpdatePackage"""
        # empty dict
        self.assertRaises(
            ValueError,
            GameUpdatePackage,
            currency=45,
            score=10,
            click_modifier=2,
            passive_gain=0,
            top_players=[{}],
        )

        # missing attributes on second dict
        self.assertRaises(
            ValueError,
            GameUpdatePackage,
            currency=45,
            score=10,
            click_modifier=2,
            passive_gain=0,
            top_players=[{"playername": "player1", "score": 10}, {}],
        )

    def test_002_LobbyStatusPackage_playerlist_validation(self):
        """test validation of players list on LobbyStatusPackage"""
        self.assertRaises(ValueError, LobbyStatusPackage, gamecode="FH12", players=[{}])  # empty dict
        # missing attributes on second dict
        self.assertRaises(ValueError, LobbyStatusPackage, gamecode="FH12", players=[{"playername": "player1", "is-ready": True}, {}])
