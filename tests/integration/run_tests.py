"""wrapper script for running integration tests"""

import coverage
import unittest
from tests.integration import ADVANCED_TESTS
from tests.integration import server_setup

def main():
    cov = coverage.Coverage()
    cov.start()

    if ADVANCED_TESTS:
        server_setup.start_server()

    try:
        suite = unittest.defaultTestLoader.discover('tests/integration')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
    finally:
        if ADVANCED_TESTS:
            server_setup.stop_server()

        cov.stop()
        cov.save()
        cov.report()


if __name__ == "__main__":
    main()
