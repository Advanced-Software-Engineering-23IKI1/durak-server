from bbc_server.packages import BasePackage

class StartGameSessionPackage(BasePackage):
    PACKAGE_TYPE = "start-game-session"
    JSON_PARAM_MAP = {
        "playername": "playername"
    }

    def __init__(self, playername: str):
        """StartGameSessionPackage
        see the package documentation for more information

        Args:
            playername (str): name of the player
        """
        self.__playername = playername

    def _generate_body_dict(self) -> dict:
        return {"playername": self.__playername}

    @property
    def playername(self) -> str:
        return self.__playername

    def __repr__(self):
        return f"StartGameSessionPackage({self.playername})"
