import unittest

import os
import pathlib
import sys

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from durak_server.packages import *
from durak_server.packages import Decoder
from durak_server.exceptions import InvalidPackageTypeException, InvalidBodyException
from durak_server.game.card import CardValue, Deck32
from json import JSONDecodeError


class DecoderTest(unittest.TestCase):

    def test_001_invalid_string(self):
        """test with a non-JSON string"""
        test_str = "some_clearly_not_json_string"
        self.assertRaises(JSONDecodeError, Decoder.deserialize, input_str=test_str)

    def test_002_invalid_package_json(self):
        """test with valid JSON but invalid package"""
        test_str = '{"some_attr": 9}'
        self.assertRaises(
            InvalidPackageTypeException, Decoder.deserialize, input_str=test_str
        )

    def test_003_invalid_package_type(self):
        """test with valid JSON with nonexistent package type"""
        test_str = '{"type": "some_made_up_type"}'
        self.assertRaises(
            InvalidPackageTypeException, Decoder.deserialize, input_str=test_str
        )

    def test_004_invalid_body(self):
        """test with valid JSON and package type but incorrect body"""
        test_str = '{"type": "start-game-session", "not_the_playername": 7}'
        self.assertRaises(InvalidBodyException, Decoder.deserialize, input_str=test_str)

    def test_005_invalid_nested_body(self):
        """test if Decoder handles a faulty nested body correctly"""
        # using string input as class does structure validation and permits creation of badly structured packages
        test_str = '{"type": "lobby-status", "body": {"gamecode": "123456", "players": [{"playername": 1}]}}'
        self.assertRaises(InvalidBodyException, Decoder.deserialize, input_str=test_str)

    def test_006_decode_ConnectToGameSessionPackage(self):
        """test decoding the ConnectToGameSessionPackage"""
        test_pkg = ConnectToGameSessionPackage(gamecode="47EC", playername="player1")
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_007_decode_ExceptionPackage(self):
        """test decoding the ExceptionPackage"""
        test_pkg = ExceptionPackage(name="myException", details={"some_detail": 17})
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_008_decode_GameStartPackage(self):
        """test decoding the GameStartPackage"""
        test_pkg = GameStartPackage()
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_009_decode_LobbyStatusPackage(self):
        """test decoding the LobbyStatusPackage"""
        test_pkg = LobbyStatusPackage(
            gamecode="AE98",
            players=[
                {
                    "playername": "player1",
                    "player_id": 10,
                    "is-ready": True,
                    "can-modify-config": False,
                }
            ],
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_010_decode_StartGameSessionPackage(self):
        """test decoding the StartGameSessionPackage"""
        test_pkg = StartGameSessionPackage(playername="player1")
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_011_decode_StatusUpdatePackage(self):
        """test decoding the StatusUpdatePackage"""
        test_pkg = StatusUpdatePackage(is_ready=True)
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_012_decode_PlayerSurrenderPackage(self):
        """test decoding the PlayerSurrenderPackage"""
        test_pkg = PlayerSurrenderPackage()
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_013_decode_EndRoutinePackage(self):
        """test decoding the EndRoutinePackage"""
        test_pkg = EndRoutinePackage([2, 3, 4, 5, 1, 8])
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_014_decode_PlayerStatusPackage(self):
        """test decoding the PlayerStatusPackage"""
        test_pkg = PlayerStatusPackage(
            [{"player_id": 2, "status": "attack"}, {"player_id": 0, "status": "defend"}]
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_014_decode_PlayerHandsUpdatePackage(self):
        """test decoding the PlayerHandsUpdatePackage"""
        test_pkg = PlayerHandsUpdatePackage(
            [1, 2, 3], [{"player_id": 2, "card_count": 5}], 32, 9, [1, 2, 3, 4]
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_014_decode_TableUpdatePackage(self):
        """test decoding the TableUpdatePackage"""
        test_pkg = TableUpdatePackage(
            table_state=[{"attack_id": 8, "from_player": 3, "defend_id": None}]
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_015_decode_GameConfigPackage(self):
        """test decoding the GameConfigPackage"""
        test_pkg = GameConfigPackage(
            cards=[[{"value": "5", "suit": "spades", "id": 3}]],
            attack_forwarding={
                "is-enabled": True,
                "exact-count-match": False,
            },
            player_card_count=7,
            dynamic_card_count_scaling=False,
            all_card_defend_early_end=False,
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_016_decode_PlayerAttackPackage(self):
        """test decoding the PlayerAttackPackage"""
        test_pkg = PlayerAttackPackage([2, 3, 4, 5, 1, 8])
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_017_decode_PlayerDefensePackage(self):
        """test decoding the PlayerDefensePackage"""
        test_pkg = PlayerDefensePackage(
            [{"attack_id": 8, "defend_id": 9}, {"attack_id": 2, "defend_id": 0}]
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_018_decode_UserGameConfigPackage(self):
        """test decoding the UserGameConfigPackage"""
        test_pkg = UserGameConfigPackage(
            card_order=[
                CardValue._7,
                CardValue._8,
                CardValue._9,
                CardValue.J,
                CardValue._10,
                CardValue.Q,
                CardValue.K,
                CardValue.A,
            ],
            attack_forwarding={
                "is-enabled": True,
                "exact-count-match": False,
            },
            player_card_count=7,
            dynamic_card_count_scaling=False,
            all_card_defend_early_end=False,
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_019_decode_LobbyJoinConfirmationPackage(self):
        """test decoding the LobbyJoinConfirmationPackage"""
        test_pkg = LobbyJoinConfirmationPackage(player_id=9)
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)
