import unittest

import os
import pathlib
import sys
import json

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from durak_server.packages import *
from durak_server.player import PlayerGameStatus


class PackageTest(unittest.TestCase):
    """class for testing packages (mainly input validation on nested structures)"""

    def test_001_LobbyStatusPackage_playerlist_validation(self):
        """test validation of players list on LobbyStatusPackage"""
        self.assertRaises(
            ValueError, LobbyStatusPackage, gamecode="FH12", players=[{}]
        )  # empty dict
        # missing attributes on second dict
        self.assertRaises(
            ValueError,
            LobbyStatusPackage,
            gamecode="FH12",
            players=[{"playername": "player1", "is-ready": True}, {}],
        )

    def test_002_PlayerStatusPackage_statuslist_validation(self):
        """test validation and internal dtype conversion of player status list on PlayerStatusPackage"""
        self.assertRaises(
            ValueError,
            PlayerStatusPackage,
            statuses=[{"player_id": 1, "status": "ready"}],
        )
        self.assertRaises(ValueError, PlayerStatusPackage, statuses=[{"player_id": 2}])
        # these should not raise
        my_package = PlayerStatusPackage(
            statuses=[{"player_id": 2, "status": "attack"}]
        )
        my_package = PlayerStatusPackage(
            statuses=[{"player_id": 0, "status": PlayerGameStatus.Attacker}]
        )

    def test_003_PlayerStatusPackage_dtype_conversion(self):
        """test internal dtype conversion from Enum to str on PlayerStatusPackage"""
        my_package = PlayerStatusPackage(
            statuses=[{"player_id": 0, "status": PlayerGameStatus.Attacker}]
        )
        send_dict = json.loads(my_package.to_json())
        self.assertEqual(send_dict["body"]["statuses"][0]["status"], "attack")

    def test_004_PlayerHandsUpdatePackage_playerhands_validation(self):
        """test validation of player hands list on PlayerHandsUpdatePackage"""
        self.assertRaises(
            ValueError,
            PlayerHandsUpdatePackage,
            hand=[1, 2, 3],
            player_hands=[{"player_id": 2}],
            draw_pile=32,
            trump=9,
            player_order=[1, 2, 3, 4],
        )

    def test_005_PlayerHandsUpdatePackage_playerhands_validation(self):
        """test validation of table state list on TableUpdatePackage"""
        self.assertRaises(
            ValueError,
            TableUpdatePackage,
            table_state=[{"attack_id": 8, "from_player": 3}],  # missing attribute
        )
        self.assertRaises(
            ValueError,
            TableUpdatePackage,
            table_state=[
                {"attack_id": 8, "from_player": 3, "defend_id": 9, "a": "b"}
            ],  # additional unallowed attr
        )
        # shouldn't raise
        my_package = TableUpdatePackage(
            table_state=[{"attack_id": 8, "from_player": 3, "defend_id": None}]
        )

    def test_006_GameConfigPackage_cards_list_validation(self):
        """test the cards list validation on the GameConfigPackage"""
        self.assertRaises(
            ValueError,
            GameConfigPackage,
            cards=[{"value": "3", "suit": "spades", "id": 3}],  # invalid as no card group
            attack_forwarding={"is-enabled": True, "exact-count-match": False},
            player_card_count=7,
            all_card_defend_early_end=False,
        )

        self.assertRaises(
            ValueError,
            GameConfigPackage,
            cards=[[{"value": "3", "suit": "spades"}]],  # inner card object missing data
            attack_forwarding={"is-enabled": True, "exact-count-match": False},
            player_card_count=7,
            all_card_defend_early_end=False,
        )

    def test_007_GameConfigPackage_attack_forwarding_dict_validation(self):
        """test the attack forwarding dict validation on the GameConfigPackage"""
        self.assertRaises(
            ValueError,
            GameConfigPackage,
            cards=[[{"value": "3", "suit": "spades", "id": 3}]],
            attack_forwarding={"is-enabled": True},  # invalid as missing a key
            player_card_count=7,
            all_card_defend_early_end=False,
        )

        self.assertRaises(
            ValueError,
            GameConfigPackage,
            cards=[[{"value": "5", "suit": "spades", "id": 3}]],
            attack_forwarding={"is-enabled": True, "exact-count-match": False, "test": 3},  # invalid because of extra key
            player_card_count=7,
            all_card_defend_early_end=False,
        )
