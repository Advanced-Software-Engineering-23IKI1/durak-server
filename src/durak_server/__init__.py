from pathlib import Path
from configparser import ConfigParser

__config_path = Path(__file__).parent.parent.parent

# read config
CONFIG = ConfigParser()
CONFIG.read(__config_path / "config.ini")

import durak_server.packages
import durak_server.tcp_client
import durak_server._typing
from durak_server.player import Player
import durak_server.tcp_server
