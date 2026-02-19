from durak_server.packages import BasePackage

class PlayerAttackPackage(BasePackage):
    PACKAGE_TYPE = "player-attack"
    JSON_PARAM_MAP = {
        "cards": "cards"
    }

    def __init__(self, cards: list[int]):
        """PlayerAttackPackage
        see the package documentation for more information

        Args:
            cards (list[int]): list of card ids
        """
        self.__cards = cards

    def _generate_body_dict(self) -> dict:
        return {"cards": self.cards}

    @property
    def cards(self) -> list[int]:
        return self.__cards

    def __repr__(self):
        return f"PlayerAttackPackage({self.cards})"
