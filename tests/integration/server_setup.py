from threading import Thread

import os
import pathlib
import sys

here = pathlib.Path(__file__).parent
repo_root_dir = here.parent.parent
# don't like this but unsure how to mitigate except for dev installation in cwd
sys.path.insert(0, os.path.join(repo_root_dir / "src"))
import bbc_server

from tests.integration import IP, PORT

SERVER = None


class TestServer:
    """small wrapper object storing the TcpServer"""
    def __init__(self):
        self.server = None
        self.server_thread = Thread(target=self.start_server_thread)
        self.server_thread.start()

    def start_server_thread(self):
        self.server = bbc_server.tcp_server.TcpServer(IP, PORT)
        self.server.start()

    def stop(self):
        self.server.stop_server()
        self.server_thread.join()


def start_server():
    global SERVER
    SERVER = TestServer()

def stop_server():
    SERVER.stop()
