Start server via docker:
`docker compose up`

Tests:
```
docker compose up unit_tests
docker compose up integration_tests
```

To use the integration tests you will need to change the tests/config.ini according
to the tests README and possibly rebuild the docker container with the `--build` flag 
