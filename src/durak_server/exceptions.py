from typing import Optional

class GameServerException(Exception):
    """Base Class for all Game Server Exceptions"""

class PackageParsingException(GameServerException):
    """Base Class for all Package Parsing Exceptions"""

class InvalidPackageTypeException(PackageParsingException):
    def __init__(self, msg: Optional[str] = None, *args, **kwargs):
        if not msg:
            msg = """Package Type is invalid"""
        super().__init__(msg, *args, **kwargs)

class InvalidBodyException(PackageParsingException):
    def __init__(self, msg: str, *args, **kwargs):
        msg = "Package Body is invalid. Exception message: " + msg
        super().__init__(msg, *args, **kwargs)
