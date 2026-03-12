import coverage
import unittest
from sys import exit


def main():
    cov = coverage.Coverage()
    cov.start()
    suite = unittest.defaultTestLoader.discover('tests/unit')
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    cov.stop()
    cov.save()
    cov.report()

    exit(not result.wasSuccessful())

if __name__ == "__main__":
    main()
