from durak_server.packages.base import BasePackage
from durak_server.packages.connect_to_game_session_package import ConnectToGameSessionPackage
from durak_server.packages.exception_package import ExceptionPackage, PackageParsingExceptionPackage, InvalidGameCodeExceptionPackage
from durak_server.packages.game_start_package import GameStartPackage
from durak_server.packages.lobby_status_package import LobbyStatusPackage
from durak_server.packages.start_game_session_package import StartGameSessionPackage
from durak_server.packages.status_update_package import StatusUpdatePackage
from durak_server.packages.player_surrender_package import PlayerSurrenderPackage
from durak_server.packages.end_routine_package import EndRoutinePackage
from durak_server.packages.player_status_package import PlayerStatusPackage
from durak_server.packages.player_hands_update_package import PlayerHandsUpdatePackage
from durak_server.packages.table_update_package import TableUpdatePackage
from durak_server.packages.game_config_package import GameConfigPackage
from durak_server.packages.player_attack_package import PlayerAttackPackage
from durak_server.packages.player_defense_package import PlayerDefensePackage
from durak_server.packages.user_game_config_package import UserGameConfigPackage

# dictionairy to map package names to actual package classes
PACKAGE_DICT = {
    "connect-to-game-session": ConnectToGameSessionPackage,
    "exception": ExceptionPackage,
    "game-start": GameStartPackage,
    "lobby-status": LobbyStatusPackage,
    "start-game-session": StartGameSessionPackage,
    "status-update": StatusUpdatePackage,
    "player-surrender": PlayerSurrenderPackage,
    "end-routine": EndRoutinePackage,
    "player-status": PlayerStatusPackage,
    "player-hands-update": PlayerHandsUpdatePackage,
    "table-update": TableUpdatePackage,
    "game-config": GameConfigPackage,
    "player-attack": PlayerAttackPackage,
    "player-defense": PlayerDefensePackage,
    "user-game-config": UserGameConfigPackage
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
    "PlayerSurrenderPackage",
    "EndRoutinePackage",
    "PlayerStatusPackage",
    "PlayerHandsUpdatePackage",
    "TableUpdatePackage",
    "GameConfigPackage",
    "PlayerAttackPackage",
    "PlayerDefensePackage",
    "UserGameConfigPackage"
]
