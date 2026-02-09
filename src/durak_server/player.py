from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from durak_server.server_logging import PlayerLogger

if TYPE_CHECKING:
    from durak_server.tcp_client import TcpClient

from durak_server._typing import GamePackage


class Player:
    def __init__(
        self,
        client: TcpClient,
        name: str = None,
        is_ready: bool = False,
        gamecode: Optional[str] = None,
    ):
        """class representing an individual player

        Args:
            client (TcpClient): the TCP Client used
            name (str, optional): player name. Defaults to None.
            is_ready (bool, optional): readiness status. Defaults to False.
            gamecode (str, optional): player game code
        """
        self._client = client
        self._name = name
        self._is_ready = is_ready
        self._points = 0
        self._gamecode = gamecode
        self._logger = PlayerLogger(self._name, self._gamecode, self._client.address[0], self._client.address[1])
        self._client.logger = self._logger  # sharing the player logger with the underlying TcpClient
        self._shop = None

    @property
    def client(self) -> TcpClient:
        return self._client

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name
        self._update_logger()

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    @is_ready.setter
    def is_ready(self, is_ready: bool) -> None:
        self._is_ready = is_ready
        self._logger.debug(f"Status changed. New status: {self._is_ready}")

    @property
    def currency(self) -> float:
        return self._currency

    @currency.setter
    def currency(self, currency: float) -> None:
        self._currency = currency

    @property
    def points(self) -> float:
        return self._points

    @points.setter
    def points(self, points: float) -> None:
        self._points = points

    @property
    def earn_rate(self) -> float:
        return self._earn_rate

    @earn_rate.setter
    def earn_rate(self, earn_rate: float) -> float:
        self._earn_rate = earn_rate

    @property
    def gamecode(self) -> str:
        return self._gamecode
    
    @gamecode.setter
    def gamecode(self, gamecode: str):
        self._gamecode = gamecode
        self._update_logger()

    @property
    def click_modifier(self) -> float:
        return self._click_modifier

    @click_modifier.setter
    def click_modifier(self, click_modifier: float) -> float:
        self._click_modifier = click_modifier


    def read_package(self, **kwargs) -> Optional[GamePackage]:
        """read a package if available (wraps TCPClient.read_package())
        If a package is invalid the next package is automatically read.

        Returns:
            Optional[GamePackage]: input package
        """
        package = self._client.read_package(**kwargs)
        if package:
            self._logger.debug(f"Read package: {str(package)}")
        return package

    def send_package(self, package: GamePackage, **kwargs) -> None:
        """send package to the Client (wraps TCPClient.send_package())

        Args:
            package (GamePackage): package to send
        """
        self._client.send_package(package=package, **kwargs)

    def _update_logger(self):
        """small function to update the logger"""
        self._logger = PlayerLogger(self._name, self.gamecode, self._client.address[0], self._client.address[1])
        self._client.logger = self._logger

    @property
    def logger(self) -> PlayerLogger:
        return self._logger
