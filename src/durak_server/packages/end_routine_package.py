from durak_server.packages import BasePackage

class EndRoutinePackage(BasePackage):
    PACKAGE_TYPE = "end-routine"
    JSON_PARAM_MAP = {
        "scoreboard": "scoreboard"
    }

    def __init__(self, scoreboard: list[int]):
        """EndRoutinePackage
        see the package documentation for more information

        Args:
            scoreboard (list[int]): list of player ids
        """
        self.__scoreboard = scoreboard

    def _generate_body_dict(self) -> dict:
        return {"scoreboard": self.scoreboard}

    @property
    def scoreboard(self) -> list[int]:
        return self.__scoreboard

    def __repr__(self):
        return f"EndRoutinePackage({self.scoreboard})"
