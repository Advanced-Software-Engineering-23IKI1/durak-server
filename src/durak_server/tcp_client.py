import socket
from typing import Optional
from bbc_server._typing import BBCPackage
from bbc_server.packages import Decoder, PackageParsingExceptionPackage
from bbc_server.server_logging import PlayerLogger
from json import JSONDecodeError
from threading import Thread
import time
from bbc_server.exceptions import InvalidPackageTypeException, InvalidBodyException

class TcpClient:
    PACKET_SEPERATOR = '\x1E'

    def __init__(self, client: socket.socket, address: socket.AddressInfo, logger: Optional[PlayerLogger] = None):
        """Creates a Tcp_client object from a given tcp socket and connection address

        Args:
            client (socket): the socket used for this connection
            address (socket.AddressInfo): the address of this connection
        """
        self._client = client
        self._client.setblocking(False)
        self.address = address

        self._text = ""  # A storage to hold read but not yet parsed text from the client
        self._package_queue = list()
        self.is_running = True

        self._outgoing_queue = list()
        self._logger = logger
        # Start a thread for sending packages to the client
        self.thread = Thread(target=self._send_message_thread)
        self.thread.start()

    @property
    def logger(self) -> Optional[PlayerLogger]:
        return self._logger
    
    @logger.setter
    def logger(self, logger: PlayerLogger):
        self._logger = logger

    def _send_message_thread(self):
        """Sends elements of the outgoing queue
        """
        while self.is_running:
            while self._outgoing_queue:
                try:
                    pkg = self._outgoing_queue.pop(0)
                    self._client.sendall((pkg + TcpClient.PACKET_SEPERATOR).encode())
                except:
                    if self._logger:
                        self._logger.info("lost connection")
                    self.is_running = False
                    return
                else:
                    self._logger.debug(f"Sent package: {pkg}")

            time.sleep(0.1)

    def shutdown(self):
        """Closes all resources used by the tcp_client
        """
        self.is_running = False
        self.thread.join()

        try:
            self._client.shutdown(socket.SHUT_RDWR)
        except:
            pass
        self._client.close()
        self._logger.debug("Closing client.")


    def has_content(self) -> bool:
        """Returns whether or not data is available from the Tcp_client

        Returns:
            bool: True if content is available, False otherwise
        """
        if not self.is_running:
            return False

        if self._package_queue:
            return True

        try:
            while TcpClient.PACKET_SEPERATOR not in self._text:
                data = self._client.recv(1024)
                if not data:
                    raise ConnectionAbortedError()
                self._text += data.decode()
        except (ConnectionResetError, ConnectionAbortedError):
            self.is_running = False
            if self._logger:
                self._logger.info("lost connection")
            return False
        except BlockingIOError:
            return False

        packages = self._text.split(TcpClient.PACKET_SEPERATOR)
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
        if not self.is_running:
            return

        self._outgoing_queue.append(content)

    def read_package(self, **kwargs) -> Optional[BBCPackage]:
        """read a package if available
        If a package is invalid the next package is automatically read.

        Returns:
            Optional[BBCPackage]: input package
        """
        package = None
        while self.has_content():
            raw_str = self.read_string()
            try:
                package = Decoder.deserialize(raw_str)
            except (JSONDecodeError, TypeError) as e:
                self.send_package(PackageParsingExceptionPackage(stage="JSON", raw_msg=str(e)))
                self._logger.debug(f"Invalid package, stage=JSON, msg={raw_str}")
            except InvalidPackageTypeException as e:
                self.send_package(PackageParsingExceptionPackage(stage="Package-Type", raw_msg=str(e)))
                self._logger.debug(f"Invalid package, stage=Package-Type, msg={raw_str}")
            except InvalidBodyException as e:
                self.send_package(PackageParsingExceptionPackage(stage="Body", raw_msg=str(e)))
                self._logger.debug(f"Invalid package, stage=Body, msg={raw_str}")

            return package



    def send_package(self, package: BBCPackage, **kwargs) -> None:
        """send package to the Client

        Args:
            package (BBCPackage): package to send
        """
        self.send_string(package.to_json())
