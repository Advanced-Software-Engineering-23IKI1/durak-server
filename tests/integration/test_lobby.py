"""integration tests for the game session and lobby logic
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
from bbc_server.packages import *

from tests.tcp_test_client import TcpTestClient
from tests.integration import IP, PORT
from tests.integration.server_setup import SERVER
import datetime

class TestLobby(unittest.TestCase):

    def test_001_create_game_session(self):
        """check if a new game session is created when the correct package is sent"""
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))
        response = None
        while not response:
            response = client.read_package()
        self.assertTrue(isinstance(response, LobbyStatusPackage))
        self.assertEqual(len(response.players), 1)
        self.assertFalse(response.players[0]["is-ready"])

    def test_002_join_game_session(self):
        """test joining a game session"""
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))
        response = None
        while not response:
            response = client.read_package()
        gamecode = response.gamecode
        client2 = TcpTestClient(IP, PORT)
        client2.send_package(ConnectToGameSessionPackage(gamecode, "player_2"))
        response = None
        loop_enter = datetime.datetime.now()
        while not response:
            response = client.read_package()
            if response:
                # i absolutely hate this but it's necessary as the package queue means that the client WILL receive outdated packages
                # This approach however is potentially blocking if the server fails to update the player packages correctly
                # the datetime check servers as a safeguard to prevent this from happening.
                if len(response.players) == 1 and datetime.datetime.now() - loop_enter < datetime.timedelta(seconds=10):
                    response = None
        self.assertEqual(len(response.players), 2)
        self.assertFalse(any([player["is-ready"] for player in response.players]))

    def test_003_lobby_updates_on_player_disconnect(self):
        """test if a lobby correctly removes a player if he disconnects"""
        client = TcpTestClient(IP, PORT)
        client.send_package(StartGameSessionPackage("player_1"))
        response = None
        while not response:
            response = client.read_package()
        gamecode = response.gamecode
        client2 = TcpTestClient(IP, PORT)
        client2.send_package(ConnectToGameSessionPackage(gamecode, "player_2"))
        time.sleep(0.5)  # give server enough time to connect the player
        client2.shutdown()
        
        loop_enter = datetime.datetime.now()
        end = False
        event_counter = 0
        while (not end) and (datetime.datetime.now() - loop_enter < datetime.timedelta(seconds=10)):
            # loop explanation: due to the queue(s) and network latency the expected behaviour is something like this:
            # player count in packages jumps to 2 at some point and drops down to 1 after (disconnect)
            response = client.read_package()
            if response:
                match len(response.players):
                    case 1:
                        if event_counter == 1:
                            event_counter = 2
                            end = True
                    case 2:
                        event_counter = 1
                    case _:
                        self.fail("unexpected length of player list")

        self.assertEqual(event_counter, 2)
