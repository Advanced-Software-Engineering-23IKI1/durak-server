from bbc_server.packages import BasePackage
from typing import Optional

class ShopPurchaseConfirmationPackage(BasePackage):
    PACKAGE_TYPE = "shop-purchase-confirmation"
    JSON_PARAM_MAP = {
        "name": "name",
        "tier": "tier"
    }

    def __init__(self, name: str, tier: Optional[int] = None):
        """ShopPurchaseConfirmationPackage
        see the package documentation for more information

        Args:
            name (str): name of the upgrade
            tier (int, optional): tier of the upgrade if a tiered upgrade
        """
        self.__name = name
        self.__tier = tier

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "name": self.__name
            }
        if self.__tier is not None:
            dict_repr["tier"] = self.__tier
        return dict_repr

    @property
    def name(self) -> str:
        return self.__name

    @property
    def tier(self) -> str:
        return self.__tier
    
    def __repr__(self):
        return f"ShopPurchaseConfirmationPackage({self.name}, {self.tier})"
