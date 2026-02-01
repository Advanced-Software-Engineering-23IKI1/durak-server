from bbc_server.packages import BasePackage
from bbc_game._typing import ShopType
from bbc_game.shop import TieredUpgrade, ClickUpgrade, GainUpgrade

class ShopBroadcastPackage(BasePackage):
    PACKAGE_TYPE = "shop-broadcast"
    JSON_PARAM_MAP = {
        "shop_entries": "shop_entries"
    }

    def __init__(self, shop_entries: list[dict]):
        self._shop_entries = shop_entries

    def _generate_body_dict(self):
        return {"shop_entries": self._shop_entries}
    
    def __repr__(self):
        return f"ShopBroadcastPackage({str(self._shop_entries)})"


def _encode_shop(shop: ShopType):

    def cast_upgrade_target(inpt):
        match inpt:
            case ClickUpgrade():
                return "click_modifier"
            case GainUpgrade():
                return "gain"

    entry_list = []
    for shop_entry in shop.shop_entries:
        entry_dict = {}
        is_single = not isinstance(shop_entry, TieredUpgrade)
        entry_dict["name"] = shop_entry.name
        entry_dict["type"] = "single" if is_single else "tiered"
        entry_dict["target"] = cast_upgrade_target(shop_entry) if is_single else cast_upgrade_target(shop_entry.upgrades[0])
        if shop_entry.description:
            entry_dict["description"] = shop_entry.description
        if is_single:
            entry_dict["price"] = shop_entry.price
        else:
            entry_dict["tiers"] = []
            for tier in shop_entry.upgrades:
                tier_dict = {}
                tier_dict["price"] = tier.price
                if tier.name:
                    tier_dict["name"] = tier.name
                if tier.description:
                    tier_dict["description"] = tier.description
                entry_dict["tiers"].append(tier_dict)

        entry_list.append(entry_dict)

    return entry_list


def create_ShopBroadcastPackage_from_shop(shop: ShopType) -> ShopBroadcastPackage:
    """create a ShopBroadcastPackage from a shop

    Args:
        shop (ShopType): the shop

    Returns:
        ShopBroadcastPackage
    """
    return ShopBroadcastPackage(_encode_shop(shop))
