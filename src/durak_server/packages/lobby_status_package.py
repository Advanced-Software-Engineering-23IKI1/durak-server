from bbc_server.packages import BasePackage

class LobbyStatusPackage(BasePackage):
    PACKAGE_TYPE = "lobby-status"
    JSON_PARAM_MAP = {
        "gamecode": "gamecode",
        "players": "players"
    }

    def __init__(self, gamecode: str, players: list[dict]):
        """LobbyStatusPackage
        see the package documentation for more information

        Args:
            gamecode (str): gamecode
            players (list[dict]): list of players with their readiness status

        Raises:
            ValueError: _description_
        """
        self.__gamecode = gamecode
        if not self.is_player_list_valid(players):
            raise ValueError("player list is not valid")
        self.__players = players

    def is_player_list_valid(self, players: list[dict]) -> bool:
        """check if player list is in the defined format
        This is done performing only structural checks.
        More information on the required strcture and data can be found in the package documentation

        Args:
            players (list[dict]): input player list

        Returns:
            bool: flag
        """
        keys = {"playername", "is-ready"}
        return all(set(player.keys()) == keys for player in players)

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "gamecode": self.__gamecode,
            "players": self.__players
        }
        return dict_repr

    @property
    def gamecode(self) -> str:
        return self.__gamecode

    @property
    def players(self) -> list[dict]:
        return self.__players

    def __repr__(self):
        return f"LobbyStatusPackage({self.gamecode}, {str(self.players)})"
