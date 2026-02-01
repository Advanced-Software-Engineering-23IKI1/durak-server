from __future__ import annotations
from bbc_server.packages import StartGameSessionPackage, ConnectToGameSessionPackage, InvalidGameCodeExceptionPackage
from bbc_server.tcp_client import TcpClient
from bbc_game.game_session import GameSession
from bbc_game.game_state import GameState
from threading import Thread
import time
import signal
import socket
from bbc_server import Player
from typing import Optional
from bbc_server.server_logging import ServerLogger

class TcpServer:
    def __init__(self, host: str, port: int):
        """Creates and starts a Tcp_server on the provided host and port

        Args:
            host (str): the host submask to start the server on (To allow global traffic, use '0.0.0.0')
            port (int): the port the server listens on
        """
        self._host = host
        self._port = port
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.bind((host, port))

        self._is_server_running = False

        self.players = []
        self.game_sessions = {}
        self._package_listener_thread = Thread(target=self._package_listener)
        self._logger = ServerLogger()


    def start(self):
        """start TcpServer"""
        self._server.listen()
        self._server.setblocking(False)
        self._is_server_running = True
        try:
            signal.signal(signal.SIGINT, self.stop_server)
        except:
            pass
        self._package_listener_thread.start()
        self._logger.info(f"Server listening on [{self._host or 'localhost'}:{self._port}]")
        self._connection_listener()


    def _connection_listener(self):
        """Loop listening for new client connections
        """
        while self._is_server_running:
            try:
                (client, address) = self._server.accept()
                self._logger.info(f"Handling new client from [{address}]")
                self.players.append(Player(TcpClient(client, address)))
            except BlockingIOError:
                time.sleep(1)

            # Remove cleaned game sessions
            cleaned_sessions = [
                code for code, session in self.game_sessions.items()
                if session.state == GameState.Cleaned
            ]
            for code in cleaned_sessions:
                del self.game_sessions[code]
                self._logger.info(f"Deleted game session with code [{code}]")

    def _package_listener(self):
        """Loop listening for packages on the players currently assigned to the Tcp_server
        """
        while self._is_server_running:
            for player in self.players:

                if not (package := player.read_package()):
                    continue

                if isinstance(package, StartGameSessionPackage):
                    # Creates a new game session and adds the current player to the session
                    player.name = package.playername
                    session = self.create_game_session()
                    player.gamecode = session.code
                    session.add_player(player)
                    self.players.remove(player)
                elif isinstance(package, ConnectToGameSessionPackage):
                    if package.gamecode in self.game_sessions.keys():
                        player.gamecode = package.gamecode
                        player.name = package.playername
                        self.game_sessions[package.gamecode].add_player(player)
                        self.players.remove(player)
                    else:
                        player.logger.info("Invalid Game Code provided.")
                        player.send_package(InvalidGameCodeExceptionPackage(package.gamecode))
                else:
                    print(f"[{player.client.address}] {package.to_json()}")


            time.sleep(0.2)

    def stop_server(self, signum: Optional[int] = None, frame: Optional = None):
        """Stops the Tcp_server and the running threads on Ctrl-C

        Args:
            signum : Value needed for Ctrl-C interception
            frame : Value needed for Ctrl-C interception
        """
        # Only stop the server, if not already stopped
        if not self._is_server_running:
            return

        self._logger.info("Stopping server ...")
        self._is_server_running = False

        for player in self.players:
            player.client.shutdown()

        for session in self.game_sessions.values():
            # Skip cleaned sessions
            if session.state == GameState.Cleaned:
                continue

            self._logger.info(f"Killing game session [{session.code}]...")
            session.state = GameState.Kill
            session.thread.join()
            session.cleanup()

        # Stop package listener
        self._logger.info("Killing main tcp server ...")
        self._package_listener_thread.join()
        self._server.close()

        self._logger.info("Server shutdown successfull.")

    def create_game_session(self) -> GameSession:
        """Creates a new game session and adds it to the game session dictionary

        Returns:
            GameSession: The newly created game session
        """
        session = GameSession()
        self.game_sessions[session.code] = session
        self._logger.info(f"Created new game session with code [{session.code}]")
        return session


if __name__ == "__main__":
    from bbc_server import CONFIG
    host = CONFIG.get("server", "HOST")
    port = int(CONFIG.get("server", "PORT").strip() or "0")

    TcpServer(host, port)
