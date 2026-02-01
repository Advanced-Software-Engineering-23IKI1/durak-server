from tests.interactive_test_client import InteractiveTestClient
from tests import TEST_CONFIG

import sys
import os
import pathlib

BBC_SERVER_DIR = pathlib.Path(__file__).parent.parent / "src"

sys.path.insert(0, os.path.join(BBC_SERVER_DIR))
sys.path.insert(0, os.path.join(pathlib.Path(__file__).parent.parent))

from bbc_server.packages import StartGameSessionPackage, ConnectToGameSessionPackage, StatusUpdatePackage

IP = str(TEST_CONFIG.get("test_server", "IP")).strip()
PORT = int(TEST_CONFIG.get("test_server", "PORT").strip())
client1 = InteractiveTestClient(IP, PORT)

client1.send_package(StartGameSessionPackage("player 1"))  # start game session
pkg = None
while not pkg:
    pkg = client1.read_package()  # wait for server to send lobby status with game code

client2 = InteractiveTestClient(IP, PORT)
client2.send_package(ConnectToGameSessionPackage(pkg.gamecode, "player 2"))  # connect 2nd client to session

# set both players' status to True
client1.send_package(StatusUpdatePackage(True))
client2.send_package(StatusUpdatePackage(True))

# make client 2 interactive
client2.make_interactive()
