from __future__ import annotations

import socket
import sys
import pathlib
import os
from typing import Optional
from json import JSONDecodeError
from threading import Thread
import logging
from tests.utils.logging import TEST_LOGGER


BBC_SERVER_DIR = pathlib.Path(__file__).parent.parent / "src"

sys.path.insert(0, os.path.join(BBC_SERVER_DIR))
sys.path.insert(0, os.path.join(pathlib.Path(__file__).parent.parent))

import bbc_server
from bbc_server.exceptions import InvalidPackageTypeException, InvalidBodyException
from bbc_server.packages import Decoder, PackageParsingExceptionPackage
from bbc_server._typing import BBCPackage


class TcpTestClient:
    PACKET_SEPERATOR = '\x1E'

    def __init__(self, ip: str, port: int):
        """Creates a Tcp_client object from a given tcp socket

        Args:
            client (socket): the socket used for this connection
        """
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client.connect((ip, port))
        self._client.setblocking(False)

        self._text = ""  # A storage to hold read but not yet parsed text from the client
        self._package_queue = list()
        self._is_running = True

    def has_content(self) -> bool:
        """Returns whether or not data is available from the Tcp_client

        Returns:
            bool: True if content is available, False otherwise
        """
        if not self._is_running:
            return False

        if self._package_queue:
            return True

        try:
            while self.PACKET_SEPERATOR not in self._text:
                data = self._client.recv(1024)
                if not data:
                    raise ConnectionAbortedError()
                self._text += data.decode()
        except (ConnectionResetError, ConnectionAbortedError):
            self._is_running = False
            TEST_LOGGER.info("client lost connection")
            return False
        except BlockingIOError:
            return False

        packages = self._text.split(self.PACKET_SEPERATOR)
        self._package_queue.extend(packages[:-1])
        self._text = packages[-1]

        return True

    def read_string(self) -> str | None:
        """Reads a string object from the Tcp_client

        Returns:
            str | None: Returns the string element if one can be read, None otherwise
        """
        if not self.has_content():
            return None

        return self._package_queue.pop(0)

    def send_string(self, content: str):
        """Sends a string object to the Tcp_client

        Args:
            content (str): The string object to send
        """
        if not self._is_running:
            return

        try:
            self._client.sendall((content + self.PACKET_SEPERATOR).encode())
        except (ConnectionResetError, ConnectionAbortedError):
            TEST_LOGGER.info("client lost connection")
            self._is_running = False

    def read_package(self, **kwargs) -> Optional[BBCPackage]:
        """read a package if available
        If a package is invalid the next package is automatically read.

        Returns:
            Optional[BBCPackage]: input package
        """
        package = None
        while self.has_content():
            try:
                package =  Decoder.deserialize(self.read_string())
            except JSONDecodeError as e:
                details = {
                    "raw_msg": str(e)
                }
                TEST_LOGGER.warning(PackageParsingExceptionPackage(stage="JSON", details=details))
            except InvalidPackageTypeException as e:
                details = {
                    "raw_msg": str(e)
                }
                TEST_LOGGER.warning(PackageParsingExceptionPackage(stage="Package-Type", details=details))
            except InvalidBodyException as e:
                details = {
                    "raw_msg": str(e)
                }
                TEST_LOGGER.warning(PackageParsingExceptionPackage(stage="Body", details=details))
            

            return package

    def send_package(self, package: BBCPackage, **kwargs) -> None:
        """send package to the Client

        Args:
            package (BBCPackage): package to send
        """
        self.send_string(package.to_json())

    def shutdown(self):
        self._is_running = False
        self._client.shutdown(socket.SHUT_RDWR)

