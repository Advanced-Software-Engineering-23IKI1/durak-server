from durak_server.packages import BasePackage

class LobbyJoinConfirmationPackage(BasePackage):
    PACKAGE_TYPE = "lobby-join-confirmation"
    JSON_PARAM_MAP = {
        "player-id": "player_id"
    }

    def __init__(self, player_id: int):
        """GameStartPackage
        see the package documentation for more information

        Args:
            player_id (int): id of the player
        """
        self.__player_id = player_id

    def _generate_body_dict(self) -> dict:
        return {
            "player-id": self.__player_id
        }
    
    @property
    def player_id(self) -> int:
        return self.__player_id

    def __repr__(self):
        return f"LobbyJoinConfirmationPackage({self.player_id})"
