# Tests

Tests are split into unit and integration tests.

There is also an interactive test client meant for testing using an terminal-based user interface for manually sending packages.
The interactive client can be used programatically and made interactive after sending packages programatically using the `make_interactive` method


### Test Setup

Integration tests and test clients require a config.ini file located at `tests/config.ini`.

The config.ini file provides configuration options for the test client and logging systems.
Integration tests can be run in one of two modes:

- non advanced: requires a server address of an already running bbc server. This can be either local or remote (in the cloud).
- advanced: launches a local server at the address and port specified in the config.

It is recommended to run the integration tests in both modes as the advanced mode provides the benefit of being able to check the internal server state while the non advanced mode provides the advantage of being able to make sure the code works as expected in a enviroment with possible high latency.

example integration file:
```ini
[test_server]
IP = 127.0.0.1
PORT = 65432
ADVANCED_TESTS = 1  # set to 1 for advanced testing mode
[test_logging]
FILE = logs/test_log.txt  # file specifically for test logs; normal server logs in advanced mode are stored in the location specified in the server's config.ini
STREAM_LEVEL = INFO
FILE_LEVEL = DEBUG
```

### Running Tests
(from repo root dir)

unit tests:
```sh
python -m tests.unit.run_tests
```

integration tests:
```sh
python -m tests.integration.run_tests
```

interactive test client:
```sh
python -m tests.interactive_test_client
```

