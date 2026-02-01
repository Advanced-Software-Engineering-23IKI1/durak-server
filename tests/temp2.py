from tests.interactive_test_client import InteractiveTestClient
from tests import TEST_CONFIG

import sys
import os
import pathlib
import time

BBC_SERVER_DIR = pathlib.Path(__file__).parent.parent / "src"

sys.path.insert(0, os.path.join(BBC_SERVER_DIR))
sys.path.insert(0, os.path.join(pathlib.Path(__file__).parent.parent))

from bbc_server.packages import *

IP = str(TEST_CONFIG.get("test_server", "IP")).strip()
PORT = int(TEST_CONFIG.get("test_server", "PORT").strip())
client = InteractiveTestClient(IP, PORT)

client.send_package(StartGameSessionPackage("player 1"))  # start game session

# set players status to True
client.send_package(StatusUpdatePackage(True))

pkg = None
while not isinstance(pkg, ShopBroadcastPackage):
    pkg = client.read_package()  # wait for server to send game stat package

client.send_package(PlayerClicksPackage(100))
client.send_package(ShopPurchaseRequestPackage("Better Clicks", 0))
time.sleep(0.5)
client.send_package(PlayerClicksPackage(100))

# make client interactive
client.make_interactive()
