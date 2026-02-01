from bbc_server.packages import BasePackage

class GameStartPackage(BasePackage):
    PACKAGE_TYPE = "game-start"
    JSON_PARAM_MAP = {}

    def __init__(self):
        """GameStartPackage
        see the package documentation for more information
        """
        pass

    def _generate_body_dict(self) -> dict:
        return {}

    def __repr__(self):
        return f"GameStartPackage()"
