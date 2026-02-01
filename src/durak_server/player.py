from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from bbc_server.server_logging import PlayerLogger

if TYPE_CHECKING:
    from bbc_server.tcp_client import TcpClient

from bbc_server._typing import BBCPackage
from bbc_game.shop import BaseShop, TieredUpgrade, ClickUpgrade, GainUpgrade
from bbc_server.packages import InvalidShopTransaction, ShopPurchaseConfirmationPackage


class Player:
    def __init__(
        self,
        client: TcpClient,
        name: str = None,
        is_ready: bool = False,
        currency: float = 0,
        earn_rate: float = 0,
        click_modifier: float = 1,
        gamecode: Optional[str] = None,
    ):
        """class representing an individual player

        Args:
            client (TcpClient): the TCP Client used
            name (str, optional): player name. Defaults to None.
            is_ready (bool, optional): readiness status. Defaults to False.
            currency (float, optional): currency. Defaults to 0.
            earn_rate (float, optional): earn_rate. Defaults to 0.
        """
        self._client = client
        self._name = name
        self._is_ready = is_ready
        self._currency = currency
        self._points = 0
        self._earn_rate = earn_rate
        self._click_modifier = click_modifier
        self._gamecode = gamecode
        self._logger = PlayerLogger(self._name, self._gamecode, self._client.address[0], self._client.address[1])
        self._client.logger = self._logger  # sharing the player logger with the underlying TcpClient
        self._shop = None

    @property
    def client(self) -> TcpClient:
        return self._client

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name
        self._update_logger()

    @property
    def is_ready(self) -> bool:
        return self._is_ready

    @is_ready.setter
    def is_ready(self, is_ready: bool) -> None:
        self._is_ready = is_ready
        self._logger.debug(f"Status changed. New status: {self._is_ready}")

    @property
    def currency(self) -> float:
        return self._currency

    @currency.setter
    def currency(self, currency: float) -> None:
        self._currency = currency

    @property
    def points(self) -> float:
        return self._points

    @points.setter
    def points(self, points: float) -> None:
        self._points = points

    @property
    def earn_rate(self) -> float:
        return self._earn_rate

    @earn_rate.setter
    def earn_rate(self, earn_rate: float) -> float:
        self._earn_rate = earn_rate

    @property
    def gamecode(self) -> str:
        return self._gamecode
    
    @gamecode.setter
    def gamecode(self, gamecode: str):
        self._gamecode = gamecode
        self._update_logger()

    @property
    def click_modifier(self) -> float:
        return self._click_modifier

    @click_modifier.setter
    def click_modifier(self, click_modifier: float) -> float:
        self._click_modifier = click_modifier

    @property
    def shop(self) -> BaseShop:
        return self._shop

    @shop.setter
    def shop(self, shop: BaseShop):
        self._shop = shop


    def read_package(self, **kwargs) -> Optional[BBCPackage]:
        """read a package if available (wraps TCPClient.read_package())
        If a package is invalid the next package is automatically read.

        Returns:
            Optional[BBCPackage]: input package
        """
        package = self._client.read_package(**kwargs)
        if package:
            self._logger.debug(f"Read package: {str(package)}")
        return package

    def send_package(self, package: BBCPackage, **kwargs) -> None:
        """send package to the Client (wraps TCPClient.send_package())

        Args:
            package (BBCPackage): package to send
        """
        self._client.send_package(package=package, **kwargs)

    def _update_logger(self):
        """small function to update the logger"""
        self._logger = PlayerLogger(self._name, self.gamecode, self._client.address[0], self._client.address[1])
        self._client.logger = self._logger

    def process_shop_transaction(self, upgrade_name: str, tier: Optional[int] = None):
        if upgrade_name not in self.shop.upgrades.keys():
            self._logger.info(f"Invalid ShopPurchaseTransaction. stage=upgrade_exists, original request: {upgrade_name=}, {tier=}.")
            self.send_package(InvalidShopTransaction("upgrade_exists", upgrade_name, tier))
            return

        upgrade = self.shop.upgrades.get(upgrade_name)
        if tier and (not isinstance(upgrade, TieredUpgrade) or tier > upgrade.max_tier or tier != upgrade.current_tier):
            self._logger.info(f"Invalid ShopPurchaseTransaction. stage=invalid_tier, original request: {upgrade_name=}, {tier=}.")
            self.send_package(InvalidShopTransaction("invalid_tier", upgrade_name, tier))
            return
        if isinstance(upgrade, TieredUpgrade):
            curr = upgrade.current_upgrade
            upgrade_price = curr.price
            if self.currency < upgrade_price:
                self._logger.info(f"Invalid ShopPurchaseTransaction. stage=price_check, original request: {upgrade_name=}, {tier=}.")
                self.send_package(InvalidShopTransaction("price_check", upgrade_name, tier))
                return
            else:
                self.currency -= upgrade_price
                if isinstance(curr, ClickUpgrade):
                    self.click_modifier = curr.apply_upgrade(self.click_modifier)
                    self._logger.debug(f"purchased upgrade {upgrade_name=}, {tier=}. New click_modifier={self.click_modifier}.")
                elif isinstance(curr, GainUpgrade):
                    self.earn_rate = curr.apply_upgrade(self.earn_rate)
                    self._logger.debug(f"purchased upgrade {upgrade_name=}, {tier=}. New earn_rate={self.earn_rate}.")
                upgrade.upgrade()
        else:
            if self.currency < upgrade.price:
                self._logger.info(f"Invalid ShopPurchaseTransaction. stage=price_check, original request: {upgrade_name=}, {tier=}.")
                self.send_package(InvalidShopTransaction("price_check", upgrade_name, tier))
                return
            self.currency -= upgrade.price
            if isinstance(upgrade, ClickUpgrade):
                self.click_modifier = upgrade.apply_upgrade(self.click_modifier)
                self._logger.debug(f"purchased upgrade {upgrade_name=}, {tier=}. New click_modifier={self.click_modifier}.")
            elif isinstance(upgrade, GainUpgrade):
                self.earn_rate = upgrade.apply_upgrade(self.earn_rate)
                self._logger.debug(f"purchased upgrade {upgrade_name=}, {tier=}. New earn_rate={self.earn_rate}.")

        self.send_package(ShopPurchaseConfirmationPackage(name=upgrade_name, tier=tier))


    @property
    def logger(self) -> PlayerLogger:
        return self._logger
