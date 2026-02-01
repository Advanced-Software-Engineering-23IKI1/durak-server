from bbc_server.packages import BasePackage
from typing import Optional

class ShopPurchaseRequestPackage(BasePackage):
    PACKAGE_TYPE = "shop-purchase-request"
    JSON_PARAM_MAP = {
        "upgrade-name": "upgrade_name",
        "tier": "tier"
    }

    def __init__(self, upgrade_name: str, tier: Optional[int] = None):
        """ShopPurchaseRequestPackage
        see the package documentation for more information

        Args:
            upgrade_name (str): name of the upgrade
            tier (int, optional): tier of the upgrade if a tiered upgrade
        """
        self.__upgrade_name = upgrade_name
        self.__tier = tier

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "upgrade-name": self.__upgrade_name
            }
        if self.__tier is not None:
            dict_repr["tier"] = self.__tier
        return dict_repr

    @property
    def upgrade_name(self) -> str:
        return self.__upgrade_name

    @property
    def tier(self) -> str:
        return self.__tier
    
    def __repr__(self):
        return f"ShopPurchaseRequestPackage({self.upgrade_name}, {self.tier})"
