"""Integration tests for testing configuration
"""

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

from tests.tcp_test_client import TcpTestClient
from tests.integration import IP, PORT, skip_if_advanced, skip_unless_advanced
from tests.integration.server_setup import SERVER

class TestBasicConnection(unittest.TestCase):

    def test_001_config_on_session_creation(self):
        """test sending config on the initial lobby creation
        """
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))
        response = None
        while not response:
            response = client.read_package()
            if isinstance(response, LobbyStatusPackage):
                response = None
        self.assertTrue(isinstance(response, GameConfigPackage))

    def test_002_config_on_session_join(self):
        """test sending config on the initial lobby creation
        """
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))
        for _ in range(2):
            response = None
            while not response:
                response = client.read_package()
            if isinstance(response, LobbyStatusPackage):
                gamecode = response.gamecode
            elif isinstance(response, GameConfigPackage):
                p_1_config = response
            else:
                raise ValueError("unknown package sent in lobby")
        
        client2 = TcpTestClient(IP, PORT)
        client2.send_package(ConnectToGameSessionPackage(gamecode=gamecode, playername="player_2"))
        response = None
        while not response:
            response = client2.read_package()
            if isinstance(response, LobbyStatusPackage):
                response = None
        self.assertTrue(isinstance(response, GameConfigPackage))
        p_2_config = response
        self.assertEqual(p_1_config.attack_forwarding, p_2_config.attack_forwarding)
        self.assertEqual(p_1_config.cards, p_2_config.cards)
        self.assertEqual(p_1_config.all_card_defend_early_end, p_2_config.all_card_defend_early_end)

