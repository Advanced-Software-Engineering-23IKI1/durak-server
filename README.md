# Durak-Server


This project implements the Server Side for the Durak Online card game.


### Docker Deployment

Start server via docker:
`docker compose up`


### Bare Metal Deployment:
Run ```main.py``` from the ```src``` directory.
Tested python versions:
3.12

Port and Host can be configured via [config.ini](./src/durak_server/config.ini)


### Development setup


Tests (Docker):
```
docker compose up unit_tests
docker compose up integration_tests
```

To use the integration tests you will need to change the tests/config.ini according
to the tests README and possibly rebuild the docker container with the `--build` flag

For bare metal testing instructions see [Test README](./tests/README.md)
