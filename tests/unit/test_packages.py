import unittest

import os
import pathlib
import sys

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from durak_server.packages import *


class PackageTest(unittest.TestCase):
    """class for testing packages (mainly input validation on nested structures)"""

    def test_001_LobbyStatusPackage_playerlist_validation(self):
        """test validation of players list on LobbyStatusPackage"""
        self.assertRaises(ValueError, LobbyStatusPackage, gamecode="FH12", players=[{}])  # empty dict
        # missing attributes on second dict
        self.assertRaises(ValueError, LobbyStatusPackage, gamecode="FH12", players=[{"playername": "player1", "is-ready": True}, {}])
