from durak_server.packages import BasePackage
from durak_server.player import PlayerGameStatus
from typing import Union

class PlayerStatusPackage(BasePackage):
    PACKAGE_TYPE = "player-status"
    JSON_PARAM_MAP = {
        "statuses": "statuses"
    }

    def __init__(self, statuses: list[dict[str, Union[int, bool]]]):
        """PlayerStatusPackage
        see the package documentation for more information

        Args:
            statuses (list[dict[str, Union[int, bool]]]): list of players with their readiness status

        Raises:
            ValueError: on invalid player list
        """
        if not self.is_status_list_valid(statuses):
            raise ValueError("player status list is not valid")
        self.__statuses = statuses

    def is_status_list_valid(self, statuses: list[dict[str, Union[int, bool]]]) -> bool:
        """check if player status list is in the defined format
        More information on the required structure and data can be found in the package documentation

        Args:
            statuses (list[dict]): input player status list

        Returns:
            bool: flag
        """
        keys = {"player_id", "status"}
        if not all(set(player.keys()) == keys for player in statuses):  # structure check
            return False
        return all((isinstance(player["status"], PlayerGameStatus) or (player["status"] in [state.value for state in PlayerGameStatus])) for player in statuses)

    def _generate_body_dict(self) -> dict:
        # convert Enum into string representation if necessary
        for player in self.__statuses:
            if isinstance(player["status"], PlayerGameStatus):
                player["status"] = player["status"].value

        dict_repr = {
            "statuses": self.__statuses
        }
        return dict_repr

    @property
    def statuses(self) -> list[dict[str, Union[int, bool]]]:
        return self.__statuses

    def __repr__(self):
        return f"PlayerStatusPackage({str(self.statuses)})"
