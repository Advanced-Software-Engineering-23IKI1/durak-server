import unittest

import os
import pathlib
import sys

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))

from bbc_server.packages import *
from bbc_server.packages import Decoder
from bbc_server.exceptions import InvalidPackageTypeException, InvalidBodyException
from json import JSONDecodeError


class DecoderTest(unittest.TestCase):

    def test_001_invalid_string(self):
        """test with a non-JSON string"""
        test_str = "some_clearly_not_json_string"
        self.assertRaises(JSONDecodeError, Decoder.deserialize, input_str=test_str)

    def test_002_invalid_package_json(self):
        """test with valid JSON but invalid package"""
        test_str = '{"some_attr": 9}'
        self.assertRaises(InvalidPackageTypeException, Decoder.deserialize, input_str=test_str)

    def test_003_invalid_package_type(self):
        """test with valid JSON with nonexistent package type"""
        test_str = '{"type": "some_made_up_type"}'
        self.assertRaises(InvalidPackageTypeException, Decoder.deserialize, input_str=test_str)

    def test_004_invalid_body(self):
        """test with valid JSON and package type but incorrect body"""
        test_str = '{"type": "start-game-session", "not_the_playername": 7}'
        self.assertRaises(InvalidBodyException, Decoder.deserialize, input_str=test_str)

    def test_005_invalid_nested_body(self):
        """test if Decoder handles a faulty nested body correctly"""
        # using string input as class does structure validation and permits creation of badly structured packages
        test_str = '{"type": "end-routine", "body": {"score": 17, "is-winner": false, "scoreboard": [{"playername": false}]}}'
        self.assertRaises(InvalidBodyException, Decoder.deserialize, input_str=test_str)

    def test_006_decode_ConnectToGameSessionPackage(self):
        """test decoding the ConnectToGameSessionPackage"""
        test_pkg = ConnectToGameSessionPackage(gamecode="47EC", playername="player1")
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_007_decode_EndRoutinePackage(self):
        """test decoding the EndRoutinePackage"""
        test_pkg = EndRoutinePackage(
            score=17,
            is_winner=False,
            scoreboard=[{"playername": "player1", "score": 1000}],
        )
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_008_decode_ExceptionPackage(self):
        """test decoding the ExceptionPackage"""
        test_pkg = ExceptionPackage(name="myException", details={"some_detail": 17})
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_009_decode_GameStartPackage(self):
        """test decoding the GameStartPackage"""
        test_pkg = GameStartPackage()
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_010_decode_GameUpdatePackage(self):
        """test decoding the GameUpdatePackage"""
        test_pkg = GameUpdatePackage(currency=10, score=25, click_modifier=2, passive_gain=0, top_players=[{"playername": "player1", "score": 25}])
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_011_decode_LobbyStatusPackage(self):
        """test decoding the LobbyStatusPackage"""
        test_pkg = LobbyStatusPackage(gamecode="AE98", players=[{"playername": "player1", "is-ready": True}])
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_012_decode_PlayerClicksPackage(self):
        """test decoding the PlayerClicksPackage"""
        test_pkg = PlayerClicksPackage(count=14)
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_012_decode_StartGameSessionPackage(self):
        """test decoding the StartGameSessionPackage"""
        test_pkg = StartGameSessionPackage(playername="player1")
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)

    def test_012_decode_StatusUpdatePackage(self):
        """test decoding the StatusUpdatePackage"""
        test_pkg = StatusUpdatePackage(is_ready=True)
        parsed_pkg = Decoder.deserialize(test_pkg.to_json())
        self.assertTrue(test_pkg == parsed_pkg)
