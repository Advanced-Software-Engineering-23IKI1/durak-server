"""Integration tests for testing configuration"""

import unittest

import os
import pathlib
import sys
import time

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent

# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))
from durak_server.packages import *
from durak_server.game.card import CardValue
from durak_server import CONFIG

from tests.tcp_test_client import TcpTestClient
from tests.integration import IP, PORT, skip_if_advanced, skip_unless_advanced
from tests.integration.server_setup import SERVER


class TestConfigHandling(unittest.TestCase):

    def test_001_config_on_session_creation(self):
        """test sending config on the initial lobby creation"""
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))
        response = None
        while not response:
            response = client.read_package()
            if isinstance(response, LobbyStatusPackage) or isinstance(
                response, LobbyJoinConfirmationPackage
            ):
                response = None
        self.assertTrue(isinstance(response, GameConfigPackage))

    def test_002_config_on_session_join(self):
        """test sending config on the initial lobby creation"""
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))
        for _ in range(3):
            response = None
            while not response:
                response = client.read_package()
            if isinstance(response, LobbyStatusPackage):
                gamecode = response.gamecode
            elif isinstance(response, GameConfigPackage):
                p_1_config = response
            elif isinstance(response, LobbyJoinConfirmationPackage):
                pass
            else:
                raise ValueError("unknown package sent in lobby")

        client2 = TcpTestClient(IP, PORT)
        client2.send_package(
            ConnectToGameSessionPackage(gamecode=gamecode, playername="player_2")
        )
        response = None
        while not response:
            response = client2.read_package()
            if isinstance(response, LobbyStatusPackage) or isinstance(
                response, LobbyJoinConfirmationPackage
            ):
                response = None
        self.assertTrue(isinstance(response, GameConfigPackage))
        p_2_config = response
        self.assertEqual(p_1_config.attack_forwarding, p_2_config.attack_forwarding)
        self.assertEqual(p_1_config.cards, p_2_config.cards)
        self.assertEqual(
            p_1_config.all_card_defend_early_end, p_2_config.all_card_defend_early_end
        )

    @skip_unless_advanced
    def test_003_permission_lobby_join(self):
        """test if the permission is checked when trying to change the GameConfig"""
        # TODO adapt for future changes to customization rulesets
        client_perm = TcpTestClient(IP, PORT)
        client_perm.send_package(StartGameSessionPackage("player_1"))
        response = None
        while not response:
            response = client_perm.read_package()
            if isinstance(response, LobbyJoinConfirmationPackage):
                response = None
        if isinstance(response, LobbyStatusPackage):
            gamecode = response.gamecode

        client_2 = TcpTestClient(IP, PORT)
        client_2.send_package(
            ConnectToGameSessionPackage(gamecode=gamecode, playername="player_2")
        )
        client_2.send_package(
            UserGameConfigPackage(
                card_order=[
                    CardValue.SEVEN,
                    CardValue.EIGHT,
                    CardValue.NINE,
                    CardValue.TEN,
                    CardValue.J,
                    CardValue.Q,
                    CardValue.K,
                    CardValue.A,
                ],
                attack_forwarding={
                    "is-enabled": True,
                    "exact-count-match": False,
                },
                player_card_count=7,
                dynamic_card_count_scaling=True,
                all_card_defend_early_end=False,
            )
        )
        response = None
        while not response:
            response = client_2.read_package()
            if (
                isinstance(response, LobbyStatusPackage)
                or isinstance(response, GameConfigPackage)
                or isinstance(response, LobbyJoinConfirmationPackage)
            ):
                response = None
        self.assertTrue(isinstance(response, ExceptionPackage))
        self.assertEqual(response.name, "PermissionDeniedException")

    def test_004_change_config_in_lobby(self):
        """test changing the config while in the lobby"""
        # TODO adapt for future changes to customization rulesets
        # [requires player based customization to be enabled]
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))

        
        card_order = [
                        CardValue.A,
                        CardValue.EIGHT,
                        CardValue.NINE,
                        CardValue.TEN,
                        CardValue.J,
                        CardValue.Q,
                        CardValue.K,
                        CardValue.SEVEN,
                    ]

        deck_type = eval(CONFIG.get("game", "DECK_TYPE"))
        if type(deck_type) == type([]):
            card_order = [deck_type[-1]] + deck_type[1:-1] + [deck_type[0]]
                    
        client.send_package(
            UserGameConfigPackage(
                card_order= card_order,
                attack_forwarding={
                    "is-enabled": True,
                    "exact-count-match": False,
                },
                player_card_count=7,
                dynamic_card_count_scaling=False,
                all_card_defend_early_end=False,
            )
        )
        incoming_packages = []
        for i in range(4):
            response = None
            while not response:
                response = client.read_package()
            incoming_packages.append(response)

        self.assertNotEqual(
            incoming_packages[2].cards[-1][0]["value"],
            incoming_packages[3].cards[-1][0]["value"],
        )
        self.assertNotEqual(
            incoming_packages[2].cards[0][0]["value"],
            incoming_packages[3].cards[0][0]["value"],
        )
        self.assertEqual(
            incoming_packages[2].cards[-1][0]["value"],
            incoming_packages[3].cards[0][0]["value"],
        )

    def test_005_dynamic_card_count_on_unknown_deck_raises(self):
        """test if the server returns an exception when a user tries to use dynamic card count scaling on an unknown deck"""
        # TODO adapt for future changes to customization rulesets
        # [requires player based customization to be enabled]
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))

        client.send_package(
            UserGameConfigPackage(
                card_order=[
                    CardValue.SIX,
                    CardValue.SEVEN,
                    CardValue.EIGHT,
                    CardValue.NINE,
                    CardValue.TEN,
                    CardValue.J,
                    CardValue.Q,
                    CardValue.K,
                    CardValue.A,
                ],
                attack_forwarding={
                    "is-enabled": True,
                    "exact-count-match": False,
                },
                player_card_count=None,
                dynamic_card_count_scaling=True,
                all_card_defend_early_end=False,
            )
        )

        incoming_packages = []
        for i in range(4):
            response = None
            while not response:
                response = client.read_package()
            incoming_packages.append(response)

        self.assertIsInstance(incoming_packages[3], ExceptionPackage)
        self.assertEqual(incoming_packages[3].name, "ConfigException")
        self.assertEqual(incoming_packages[3].details["msg"], "Card Count scaling is not possible for Deck set")
