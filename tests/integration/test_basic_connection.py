"""Integration tests for testing basic connection logic and error handling
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
from tests.integration import IP, PORT, skip_if_advanced, skip_unless_advanced
from tests.integration.server_setup import SERVER

class TestBasicConnection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_client = TcpTestClient(IP, PORT)

    def test_001_invalid_string(self):
        """test sending a non-valid string"""
        self.test_client.send_string("some_string")
        response = None
        while not response:
            response = self.test_client.read_package()
        self.assertTrue(isinstance(response, ExceptionPackage))
        self.assertEqual(response.name, "PackageParsingException")
        self.assertEqual(response.details["stage"], "JSON")

    def test_002_invalid_package_json(self):
        """test with valid JSON but invalid package"""
        self.test_client.send_string('{"some_attr": 9}')
        response = None
        while not response:
            response = self.test_client.read_package()
        self.assertTrue(isinstance(response, ExceptionPackage))
        self.assertEqual(response.name, "PackageParsingException")
        self.assertEqual(response.details["stage"], "Package-Type")

    def test_003_invalid_package_type(self):
        """test with valid JSON with nonexistent package type"""
        self.test_client.send_string('{"type": "some_made_up_type"}')
        response = None
        while not response:
            response = self.test_client.read_package()
        self.assertTrue(isinstance(response, ExceptionPackage))
        self.assertEqual(response.name, "PackageParsingException")
        self.assertEqual(response.details["stage"], "Package-Type")

    def test_004_invalid_body(self):
        """test with valid JSON with nonexistent package type"""
        self.test_client.send_string('{"type": "start-game-session", "not_the_playername": 7}')
        response = None
        while not response:
            response = self.test_client.read_package()
        self.assertTrue(isinstance(response, ExceptionPackage))
        self.assertEqual(response.name, "PackageParsingException")
        self.assertEqual(response.details["stage"], "Body")

    @skip_unless_advanced
    def test_005_client_present_in_player_list(self):
        """check if the client is correctly added to the server player list"""
        self.assertEqual(len(SERVER.server.players), 1)

    @skip_unless_advanced
    def test_006_client_disconnect_detected(self):
        """check if client disconnects are handled correctly"""
        second_client = TcpTestClient(IP, PORT)
        time.sleep(1)
        self.assertEqual(len(SERVER.server.players), 2)
        second_client.shutdown()
        time.sleep(1)
        self.assertFalse(SERVER.server.players[-1].client.is_running)

    @classmethod
    def tearDownClass(cls):
        cls.test_client.shutdown()
