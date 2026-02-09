from pathlib import Path
from configparser import ConfigParser

__here = Path(__file__).parent

# read config
CONFIG = ConfigParser()
CONFIG.read(__here / "config.ini")

import durak_server.packages
import durak_server.tcp_client
import durak_server._typing
from durak_server.player import Player
import durak_server.tcp_server
