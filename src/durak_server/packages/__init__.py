from bbc_server.packages.base import BasePackage
from bbc_server.packages.connect_to_game_session_package import ConnectToGameSessionPackage
from bbc_server.packages.end_routine_package import EndRoutinePackage
from bbc_server.packages.exception_package import ExceptionPackage, PackageParsingExceptionPackage, InvalidGameCodeExceptionPackage, InvalidShopTransaction
from bbc_server.packages.game_start_package import GameStartPackage
from bbc_server.packages.game_update_package import GameUpdatePackage
from bbc_server.packages.lobby_status_package import LobbyStatusPackage
from bbc_server.packages.player_clicks_package import PlayerClicksPackage
from bbc_server.packages.start_game_session_package import StartGameSessionPackage
from bbc_server.packages.status_update_package import StatusUpdatePackage
from bbc_server.packages.shop_broadcast_package import ShopBroadcastPackage, create_ShopBroadcastPackage_from_shop
from bbc_server.packages.shop_purchase_confirmation_package import ShopPurchaseConfirmationPackage
from bbc_server.packages.shop_purchase_request_package import ShopPurchaseRequestPackage

# dictionairy to map package names to actual package classes
PACKAGE_DICT = {
    "connect-to-game-session": ConnectToGameSessionPackage,
    "end-routine": EndRoutinePackage,
    "exception": ExceptionPackage,
    "game-start": GameStartPackage,
    "game-update": GameUpdatePackage,
    "lobby-status": LobbyStatusPackage,
    "player-clicks": PlayerClicksPackage,
    "start-game-session": StartGameSessionPackage,
    "status-update": StatusUpdatePackage,
    "shop-broadcast": ShopBroadcastPackage,
    "shop-purchase-confirmation": ShopPurchaseConfirmationPackage,
    "shop-purchase-request": ShopPurchaseRequestPackage
}


from bbc_server.packages import decoder as Decoder

__all__ = [
    "ConnectToGameSessionPackage",
    "EndRoutinePackage",
    "ExceptionPackage",
    "PackageParsingExceptionPackage",
    "InvalidGameCodeExceptionPackage",
    "InvalidShopTransaction",
    "GameStartPackage",
    "GameUpdatePackage",
    "LobbyStatusPackage",
    "PlayerClicksPackage",
    "StartGameSessionPackage",
    "StatusUpdatePackage",
    "ShopBroadcastPackage",
    "create_ShopBroadcastPackage_from_shop",
    "ShopPurchaseConfirmationPackage",
    "ShopPurchaseRequestPackage"
]
