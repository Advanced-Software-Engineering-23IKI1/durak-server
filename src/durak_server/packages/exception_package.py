from bbc_server.packages import BasePackage
from typing import Optional

class ExceptionPackage(BasePackage):
    PACKAGE_TYPE = "exception"
    JSON_PARAM_MAP = {
        "name": "name",
        "details": "details"
    }

    def __init__(self, name: str, details: Optional[dict] = None):
        """ExceptionPackage
        see the package documentation for more information

        Args:
            name (str): name of the exception
            details (dict): dict with more information
        """
        self.__name = name
        if not details:
            details = {}
        self.__details = details

    def _generate_body_dict(self) -> dict:
        dict_repr = {
            "name": self.__name,
            "details": self.__details
        }
        return dict_repr

    @property
    def name(self) -> str:
        return self.__name

    @property
    def details(self) -> dict:
        return self.__details

    def __repr__(self):
        return f"ExceptionPackage({self.name}, {str(self.details)})"


class PackageParsingExceptionPackage(ExceptionPackage):
    """Wrapper Class for Package Parsing Exceptions

    Args:
        stage (str): package Parsing stage at which exception occured
        details (Optional[dict], optional): additional details. Defaults to None.
    """
    def __init__(self, stage: str, raw_msg: str, details: Optional[dict] = None):
        if not details:
            details = {}
        self._stage = stage
        self._raw_msg = raw_msg
        self._details = details
        details = {
            "stage": stage,
            "raw_msg": raw_msg,
            **details
        }
        super().__init__("PackageParsingException", details)

    def __repr__(self):
        return f"PackageParsingExceptionPackage({self._stage}, {str(self._details)})"


class InvalidGameCodeExceptionPackage(ExceptionPackage):
    """Wrapper Class for Invalid GameCodes

    Args:
        code (str): the gamecode provided
        details (Optional[dict], optional): additional details. Defaults to None.
    """
    def __init__(self, code: str, details: Optional[dict] = None):
        if not details:
            details = {}
        self._code = code
        self._details = details
        details = {
            "code": code,
            **details
        }
        super().__init__("InvalidGameCodeException", details)

    def __repr__(self):
        return f"InvalidGameCodeExceptionPackage({self._code}, {str(self._details)})"


class InvalidShopTransaction(ExceptionPackage):

    def __init__(self, stage: str, upgrade_name: str, upgrade_tier: Optional[str] = None, details: Optional[dict] = None):
        if not details:
            details = {}
        self._stage = stage
        self._upgrade_name = upgrade_name
        self._upgrade_tier = upgrade_tier
        details = {
            "stage": stage,
            "upgrade_name": upgrade_name,
            **details
        }
        if upgrade_tier is not None:
            details["upgrade_tier"] = upgrade_tier
        super().__init__("InvalidShopTransaction", details)

    def __repr__(self):
        return f"InvalidShopTransaction({self._stage}, {self._upgrade_name}, {self._upgrade_tier}, {self._details})"
