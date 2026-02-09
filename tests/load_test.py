from tests.interactive_test_client import InteractiveTestClient
from tests import TEST_CONFIG

import sys
import os
import time
import pathlib

durak_server_DIR = pathlib.Path(__file__).parent.parent / "src"

sys.path.insert(0, os.path.join(durak_server_DIR))
sys.path.insert(0, os.path.join(pathlib.Path(__file__).parent.parent))

from durak_server.packages import StartGameSessionPackage, ConnectToGameSessionPackage, StatusUpdatePackage, PlayerClicksPackage

IP = str(TEST_CONFIG.get("test_server", "IP")).strip()
PORT = int(TEST_CONFIG.get("test_server", "PORT").strip())
client1 = InteractiveTestClient(IP, PORT)

client1.send_package(StartGameSessionPackage("player X"))  # start game session
pkg = None
while not pkg:
    pkg = client1.read_package()  # wait for server to send lobby status with game code


clients = [InteractiveTestClient(IP, PORT) for _ in range(30)]
for idx, client in enumerate(clients):
    print("debug")
    time.sleep(0.05)
    client.send_package(ConnectToGameSessionPackage(pkg.gamecode, f"player {idx}"))
    time.sleep(0.05)
    client.send_package(StatusUpdatePackage(True))


# main loop
while True:
    time.sleep(0.1)
    print("out")
    for idx, client in enumerate(clients):
        client.send_package(PlayerClicksPackage(100))
