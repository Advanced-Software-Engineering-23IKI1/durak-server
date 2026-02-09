import unittest
import tests
from tests import TEST_CONFIG


IP = str(TEST_CONFIG.get("test_server", "IP")).strip()
PORT = int(TEST_CONFIG.get("test_server", "PORT").strip())
ADVANCED_TESTS = bool(int(TEST_CONFIG.get("test_server", "ADVANCED_TESTS").strip()))

skip_if_advanced = unittest.skipIf(ADVANCED_TESTS, "skip if in advanced mode")
skip_unless_advanced = unittest.skipUnless(ADVANCED_TESTS, "only runs in advanced mode")
