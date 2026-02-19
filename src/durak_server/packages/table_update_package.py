from durak_server.packages import BasePackage
from typing import Optional

class TableUpdatePackage(BasePackage):
    PACKAGE_TYPE = "table-update"
    JSON_PARAM_MAP = {
        "table-state": "table_state"
    }

    def __init__(self, table_state: list[dict[str, Optional[int]]]):
        """TableUpdatePackage
        see the package documentation for more information

        Args:
            table_state (list[dict[str, Optional[int]]]): list of card pairs as described in the design

        Raises:
            ValueError: on invalid table_state
        """
        if not self.is_table_state_valid(table_state):
            raise ValueError("table_state is not valid")
        self.__table_state = table_state

    def is_table_state_valid(self, table_state: list[dict[str, Optional[int]]]) -> bool:
        """check if table_state list is in the defined format
        This is performing only structural checks.
        More information on the required structure and data can be found in the package documentation

        Args:
            table_state (list[dict[str, Optional[int]]]): input table_state list

        Returns:
            bool: flag
        """
        keys = {"attack_id", "from_player", "defend_id"}
        return all(set(cardpair.keys()) == keys for cardpair in table_state)

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "table-state": self.__table_state
        }
        return dict_repr

    @property
    def table_state(self) -> list[dict[str, Optional[int]]]:
        return self.__table_state

    def __repr__(self):
        return f"TableUpdatePackage({str(self.table_state)})"
