"""integration tests for game start routine behavior"""

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
from tests.integration import IP, PORT, ADVANCED_TESTS
from tests.integration import server_setup


class TestGameStartRoutine(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls._started_local_server = False
		if ADVANCED_TESTS and server_setup.SERVER is None:
			server_setup.start_server()
			# give the server thread time to start listening
			time.sleep(1.5)
			cls._started_local_server = True

	@classmethod
	def tearDownClass(cls):
		if cls._started_local_server and server_setup.SERVER is not None:
			server_setup.stop_server()

	def _wait_for_package_type(
		self,
		client: TcpTestClient,
		package_type: type,
		timeout_s: float = 8.0,
	):
		start = time.monotonic()
		while time.monotonic() - start < timeout_s:
			package = client.read_package()
			if isinstance(package, package_type):
				return package
			time.sleep(0.05)
		return None

	def _wait_for_lobby_status(self, client: TcpTestClient, timeout_s: float = 5.0):
		return self._wait_for_package_type(client, LobbyStatusPackage, timeout_s=timeout_s)

	def _wait_for_game_config(self, client: TcpTestClient, timeout_s: float = 5.0):
		return self._wait_for_package_type(client, GameConfigPackage, timeout_s=timeout_s)

	def _safe_shutdown(self, client: TcpTestClient):
		try:
			client.shutdown()
		except OSError:
			pass

	def _start_two_player_ready_game(self):
		client_1 = TcpTestClient(IP, PORT)
		client_2 = TcpTestClient(IP, PORT)

		client_1.send_package(StartGameSessionPackage("player_1"))
		lobby_pkg = self._wait_for_lobby_status(client_1)
		self.assertIsNotNone(lobby_pkg)
		gamecode = lobby_pkg.gamecode

		client_2.send_package(ConnectToGameSessionPackage(gamecode, "player_2"))
		self.assertIsNotNone(self._wait_for_lobby_status(client_2))

		config_1 = self._wait_for_game_config(client_1)
		config_2 = self._wait_for_game_config(client_2)

		client_1.send_package(StatusUpdatePackage(True))
		client_2.send_package(StatusUpdatePackage(True))

		start_1 = self._wait_for_package_type(client_1, GameStartPackage, timeout_s=5.0)
		start_2 = self._wait_for_package_type(client_2, GameStartPackage, timeout_s=5.0)

		self.assertIsNotNone(start_1)
		self.assertIsNotNone(start_2)

		return client_1, client_2, config_1, config_2

	def test_001_all_players_ready_starts_game(self):
		"""game should start once all players are ready"""
		client_1 = TcpTestClient(IP, PORT)
		client_2 = TcpTestClient(IP, PORT)
		try:
			client_1.send_package(StartGameSessionPackage("player_1"))
			lobby_pkg = self._wait_for_lobby_status(client_1)
			self.assertIsNotNone(lobby_pkg)
			gamecode = lobby_pkg.gamecode

			client_2.send_package(ConnectToGameSessionPackage(gamecode, "player_2"))
			self.assertIsNotNone(self._wait_for_lobby_status(client_2))

			# set all players ready
			client_1.send_package(StatusUpdatePackage(True))
			client_2.send_package(StatusUpdatePackage(True))

			start_1 = self._wait_for_package_type(client_1, GameStartPackage, timeout_s=5.0)
			start_2 = self._wait_for_package_type(client_2, GameStartPackage, timeout_s=5.0)

			self.assertIsNotNone(start_1)
			self.assertIsNotNone(start_2)

		finally:
			client_1.shutdown()
			client_2.shutdown()

	def test_002_game_does_not_start_if_not_everyone_ready(self):
		"""game should not start while at least one player is not ready"""
		client_1 = TcpTestClient(IP, PORT)
		client_2 = TcpTestClient(IP, PORT)
		try:
			client_1.send_package(StartGameSessionPackage("player_1"))
			lobby_pkg = self._wait_for_lobby_status(client_1)
			self.assertIsNotNone(lobby_pkg)

			client_2.send_package(ConnectToGameSessionPackage(lobby_pkg.gamecode, "player_2"))
			self.assertIsNotNone(self._wait_for_lobby_status(client_2))

			# only one player ready
			client_1.send_package(StatusUpdatePackage(True))

			start_1 = self._wait_for_package_type(client_1, GameStartPackage, timeout_s=2.0)
			start_2 = self._wait_for_package_type(client_2, GameStartPackage, timeout_s=2.0)

			self.assertIsNone(start_1)
			self.assertIsNone(start_2)
		finally:
			self._safe_shutdown(client_1)
			self._safe_shutdown(client_2)

	def test_003_game_start_routine_sends_player_hands_update(self):
		"""after game start, each player should receive a hands update package"""
		client_1 = None
		client_2 = None
		try:
			client_1, client_2, _, _ = self._start_two_player_ready_game()

			hands_1 = self._wait_for_package_type(client_1, PlayerHandsUpdatePackage, timeout_s=4.0)
			hands_2 = self._wait_for_package_type(client_2, PlayerHandsUpdatePackage, timeout_s=4.0)

			self.assertIsNotNone(hands_1)
			self.assertIsNotNone(hands_2)
		finally:
			if client_1:
				self._safe_shutdown(client_1)
			if client_2:
				self._safe_shutdown(client_2)

	def test_004_game_start_routine_sets_single_attacker_status(self):
		"""player status update should contain exactly one attacker at game start"""
		client_1 = None
		client_2 = None
		try:
			client_1, client_2, _, _ = self._start_two_player_ready_game()

			status_1 = self._wait_for_package_type(client_1, PlayerStatusPackage, timeout_s=4.0)
			status_2 = self._wait_for_package_type(client_2, PlayerStatusPackage, timeout_s=4.0)

			self.assertIsNotNone(status_1)
			self.assertIsNotNone(status_2)
			self.assertEqual(len(status_1.statuses), 2)
			self.assertEqual(len(status_2.statuses), 2)

			attacker_count_1 = sum(
				1 for player in status_1.statuses if player["status"] == "attack"
			)
			attacker_count_2 = sum(
				1 for player in status_2.statuses if player["status"] == "attack"
			)

			self.assertEqual(attacker_count_1, 1)
			self.assertEqual(attacker_count_2, 1)
		finally:
			if client_1:
				self._safe_shutdown(client_1)
			if client_2:
				self._safe_shutdown(client_2)

	def test_005_game_start_routine_distributes_cards_consistently(self):
		"""card distribution metadata should be consistent between both players"""
		client_1 = None
		client_2 = None
		try:
			client_1, client_2, config_1, _ = self._start_two_player_ready_game()

			hands_1 = self._wait_for_package_type(client_1, PlayerHandsUpdatePackage, timeout_s=4.0)
			hands_2 = self._wait_for_package_type(client_2, PlayerHandsUpdatePackage, timeout_s=4.0)

			self.assertIsNotNone(hands_1)
			self.assertIsNotNone(hands_2)
			self.assertEqual(len(hands_1.player_hands), 1)
			self.assertEqual(len(hands_2.player_hands), 1)

			if config_1 is not None:
				self.assertEqual(len(hands_1.hand), config_1.player_card_count)
				self.assertEqual(len(hands_2.hand), config_1.player_card_count)

			self.assertEqual(hands_1.player_hands[0]["card_count"], len(hands_2.hand))
			self.assertEqual(hands_2.player_hands[0]["card_count"], len(hands_1.hand))

			# Total cards: player hands + draw pile (trump is on bottom of draw pile)
			total_cards_from_client_1 = len(hands_1.hand) + len(hands_2.hand) + hands_1.draw_pile
			self.assertIn(total_cards_from_client_1, [32, 52])
		finally:
			if client_1:
				self._safe_shutdown(client_1)
			if client_2:
				self._safe_shutdown(client_2)
    
if __name__ == "__main__":
    unittest.main()

