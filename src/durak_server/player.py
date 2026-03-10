from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from enum import Enum
from durak_server.server_logging import PlayerLogger

if TYPE_CHECKING:
    from durak_server.tcp_client import TcpClient

from durak_server._typing import GamePackage


class PlayerGameStatus(str, Enum):
    Attacker = "attack",
    Defender = "defend",
    Finished = "finished",
    Unknown = "unknown"


class Player:
    def __init__(
        self,
        client: TcpClient,
        player_id: int = None,
        name: str = None,
        is_ready: bool = False,
        gamecode: Optional[str] = None,
    ):
        """class representing an individual player

        Args:
            client (TcpClient): the TCP Client used
            player_id (int, optional): player id. Defaults to the memory address
            name (str, optional): player name. Defaults to None.
            is_ready (bool, optional): readiness status. Defaults to False.
            gamecode (str, optional): player game code
        """
        self._client = client
        if player_id is None:
            self._player_id = id(self)
        else:
            self._player_id = player_id
        self._name = name
        self._is_ready = is_ready
        self._gamecode = gamecode
        self._logger = PlayerLogger(self._name, self._gamecode, self._client.address[0], self._client.address[1])
        self._client.logger = self._logger  # sharing the player logger with the underlying TcpClient
        self._player_game_status = PlayerGameStatus.Unknown
        self._hand = []
        self._can_modify_config = False

    @property
    def client(self) -> TcpClient:
        return self._client
    
    @property
    def player_id(self)-> int:
        return self._player_id

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
    def gamecode(self) -> str:
        return self._gamecode
    
    @gamecode.setter
    def gamecode(self, gamecode: str):
        self._gamecode = gamecode
        self._update_logger()

    @property
    def hand(self) -> list[int]:
        return self._hand
    
    @hand.setter
    def hand(self, hand: list[int]):
        self._hand = hand
        
    @property
    def can_modify_config(self) -> bool:
        return self._can_modify_config
    
    @can_modify_config.setter
    def can_modify_config(self, flag: bool):
        self._can_modify_config = flag

    @property
    def game_status(self) -> PlayerGameStatus:
        return self._player_game_status

    @game_status.setter
    def game_status(self, status: PlayerGameStatus):
        self._player_game_status = status

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
