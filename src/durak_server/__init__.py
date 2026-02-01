from pathlib import Path
from configparser import ConfigParser

__here = Path(__file__).parent

# read config
CONFIG = ConfigParser()
CONFIG.read(__here / "config.ini")

import bbc_server.packages
import bbc_server.tcp_client
import bbc_server._typing
from bbc_server.player import Player
import bbc_server.tcp_server
