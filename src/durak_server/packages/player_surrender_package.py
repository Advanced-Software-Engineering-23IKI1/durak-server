from durak_server.packages import BasePackage

class PlayerSurrenderPackage(BasePackage):
    PACKAGE_TYPE = "player-surrender"
    JSON_PARAM_MAP = {}

    def __init__(self):
        """PlayerSurrenderPackage
        see the package documentation for more information
        """
        pass

    def _generate_body_dict(self) -> dict:
        return {}

    def __repr__(self):
        return f"PlayerSurrenderPackage()"
