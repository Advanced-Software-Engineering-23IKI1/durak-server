from durak_server.packages import BasePackage

class PlayerDefensePackage(BasePackage):
    PACKAGE_TYPE = "player-defense"
    JSON_PARAM_MAP = {
        "defense": "defense"
    }

    def __init__(self, defense: list[dict[str, int]]):
        """PlayerDefensePackage
        see the package documentation for more information

        Args:
            defense (list[dict[str, int]]): list of card pairs as described in the design

        Raises:
            ValueError: on invalid defense
        """
        if not self.is_defense_list_valid(defense):
            raise ValueError("defense is not valid")
        self.__defense = defense

    def is_defense_list_valid(self, defense: list[dict[str, int]]) -> bool:
        """check if defense list is in the defined format
        This is performing only structural checks.
        More information on the required structure and data can be found in the package documentation

        Args:
            defense (list[dict[str, int]]): input defense list

        Returns:
            bool: flag
        """
        keys = {"attack_id", "defend_id"}
        return all(set(cardpair.keys()) == keys for cardpair in defense)

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "defense": self.__defense
        }
        return dict_repr

    @property
    def defense(self) -> list[dict[str, int]]:
        return self.__defense

    def __repr__(self):
        return f"PlayerDefensePackage({self.defense})"
