import sys
import os
import pathlib
from configparser import ConfigParser

here = pathlib.Path(__file__).parent

# read config
TEST_CONFIG = ConfigParser()
TEST_CONFIG.read(here / "config.ini")


