from durak_server.packages.base import BasePackage
from durak_server.packages.connect_to_game_session_package import ConnectToGameSessionPackage
from durak_server.packages.exception_package import ExceptionPackage, PackageParsingExceptionPackage, InvalidGameCodeExceptionPackage
from durak_server.packages.game_start_package import GameStartPackage
from durak_server.packages.lobby_status_package import LobbyStatusPackage
from durak_server.packages.start_game_session_package import StartGameSessionPackage
from durak_server.packages.status_update_package import StatusUpdatePackage

# dictionairy to map package names to actual package classes
PACKAGE_DICT = {
    "connect-to-game-session": ConnectToGameSessionPackage,
    "exception": ExceptionPackage,
    "game-start": GameStartPackage,
    "lobby-status": LobbyStatusPackage,
    "start-game-session": StartGameSessionPackage,
    "status-update": StatusUpdatePackage,
}


from durak_server.packages import decoder as Decoder

__all__ = [
    "ConnectToGameSessionPackage",
    "ExceptionPackage",
    "PackageParsingExceptionPackage",
    "InvalidGameCodeExceptionPackage",
    "GameStartPackage",
    "LobbyStatusPackage",
    "StartGameSessionPackage",
    "StatusUpdatePackage",
]
