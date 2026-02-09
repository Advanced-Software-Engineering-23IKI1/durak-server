"""logging for the tests"""

from tests import TEST_CONFIG
import logging
import pathlib
import os

formatter = logging.Formatter(
    fmt="[%(asctime)s.%(msecs)03d] [%(levelname)s] [source=%(source)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(str(TEST_CONFIG.get("test_logging", "STREAM_LEVEL")))

filepath = pathlib.Path(str(TEST_CONFIG.get("test_logging", "FILE")))
if not os.path.isfile(filepath):
    dir = filepath.parent
    dir.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(filepath)
stream_handler.setFormatter(formatter)
file_handler.setLevel(str(TEST_CONFIG.get("test_logging", "FILE_LEVEL")))

TEST_LOGGER = logging.getLogger("TEST_LOGGER")
TEST_LOGGER.setLevel(logging.DEBUG)
TEST_LOGGER.addHandler(stream_handler)
TEST_LOGGER.addHandler(file_handler)
