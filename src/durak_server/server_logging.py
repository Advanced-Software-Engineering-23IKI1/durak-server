"""logging for the BBC server"""
import logging
import sys
import pathlib
from typing import Optional
from bbc_server import CONFIG
import os


class BaseAdapter(logging.LoggerAdapter):
    """BaseAdapter for specialized adapters

    Args:
        logger (logging.Logger, optional): logger to use. Defaults to None.
        source (str, optional): source of the log. Defaults to "Unknown".
    """
    def __init__(self, logger: Optional[logging.Logger] = None, source: str = "Unknown", **kwargs):
        context = {
            "raw_source": source,
            "details": kwargs
        }
        super().__init__(logger or logging.getLogger("main"), context)

    def process(self, msg, kwargs):
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs


class ServerLogger(BaseAdapter):
    """Adapater for the main server

    Args:
        logger (logging.Logger, optional): logger. Defaults to None.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger, source="Server")


class SessionLogger(BaseAdapter):
    """Adapter for individual game sessions

    Args:
        gamecode (Optional[str], optional): code of the game session. Defaults to None.
        logger (Optional[logging.Logger], optional): logger. Defaults to None.
    """

    def __init__(self, gamecode: Optional[str] = None, logger: Optional[logging.Logger] = None):
        super().__init__(logger, source="Session", gamecode=gamecode)


class PlayerLogger(BaseAdapter):
    """Adapter for individual players

    Args:
        name (Optional[str], optional): player name. Defaults to None.
        gamecode (Optional[str], optional): code of the game session the player is associated with. Defaults to None.
        ip (Optional[str], optional): ip of the player. Defaults to None.
        port (Optional[int], optional): port of the player. Defaults to None.
        logger (Optional[logging.Logger], optional): logger. Defaults to None.
    """

    def __init__(self, name: Optional[str] = None, gamecode: Optional[str] = None, ip: Optional[str] = None, port: Optional[int] = None, logger: Optional[logging.Logger] = None):
        super().__init__(logger, source="Player", name=name, session=gamecode, ip=ip, port=port)


class DetailedFormatter(logging.Formatter):
    """Formatter for detailed logging"""

    def format(self, record):
        if not hasattr(record, "raw_source"):
            record.raw_source = "Unknown"
        if not hasattr(record, "details"):
            record.details = {}

        if record.details:
            args = ", ".join(f"{k}={str(v)}" for k, v in record.details.items())
            record.source = f"{record.raw_source}({args})"
        else:
            record.source = record.raw_source

        return super().format(record)


class UnknownSourceFilter(logging.Filter):
    """Filter out logs that come from unknown sources."""

    def filter(self, record: logging.LogRecord) -> bool:
        raw_source = getattr(record, "raw_source", "Unknown")
        return raw_source != "Unknown"


formatter = DetailedFormatter(
    fmt="[%(asctime)s.%(msecs)03d] [%(levelname)s] [source=%(source)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(str(CONFIG.get("logging", "STREAM_LEVEL")))

filepath = pathlib.Path(str(CONFIG.get("logging", "FILE")))
if not os.path.isfile(filepath):
    dir = filepath.parent
    dir.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(str(CONFIG.get("logging", "FILE")))
file_handler.setFormatter(formatter)
file_handler.setLevel(str(CONFIG.get("logging", "FILE_LEVEL")))


filter = UnknownSourceFilter()
stream_handler.addFilter(filter)
file_handler.addFilter(filter)


ROOT_LOGGER = logging.getLogger()
ROOT_LOGGER.setLevel(logging.DEBUG)
ROOT_LOGGER.addHandler(stream_handler)
ROOT_LOGGER.addHandler(file_handler)
