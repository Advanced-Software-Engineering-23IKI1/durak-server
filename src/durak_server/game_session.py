from durak_server.game_state import GameState
from durak_server.game_code import generate_game_code, unregister_game_code
import durak_server.packages
from threading import Thread
from durak_server import Player
from durak_server.server_logging import SessionLogger
import durak_server
import time
import durak_server.config
from durak_server._typing import GamePackage

import durak_server.packages

class GameSession:
    def __init__(self):
        """Generates a new empty game session with a newly generated game code
        """
        self.code = generate_game_code()
        self.players: list[Player] = []
        self.state = GameState.Preperation

        self.game_config = durak_server.config.default_game_config
        if self.game_config.player_card_count is None:
            self.__dynamic_config = True
        else:
            self.__dynamic_config = False
        self.__player_count_has_changed = True

        # Start the game lobby loop
        self.thread = Thread(target=self.lobby_loop)
        self.thread.start()
        self._logger = SessionLogger(gamecode=self.code)

    def update_player_list(self):
        player_list_len = len(self.players)
        self.players = [player for player in self.players if player.client.is_running]
        if len(self.players) != player_list_len:
            self._send_status_update()
            self.__player_count_has_changed = True

    def broadcast(self, package: GamePackage):
        """broadcast package to all players"""
        self.update_player_list()
        for player in self.players:
            player.send_package(package=package)

    def _send_status_update(self):
        if self.state is GameState.Preperation:
            player_list = [
                {"playername": inner_player.name, "player_id": inner_player.player_id, "is-ready": inner_player.is_ready}
                for inner_player in self.players]
            self.broadcast(durak_server.packages.LobbyStatusPackage(
                        self.code,
                        players=player_list
                    ))
    def _update_config(self) -> bool:
        self.update_player_list()
        mapping_dict = durak_server.config.CARDCOUNT_MAPPING.get(self.game_config.deck)
        player_card_count = mapping_dict.get(len(self.players))
        if player_card_count is None:
            raise ValueError("player count too high for provided config")
        self.game_config.player_card_count = player_card_count
        self._send_config()

    def _send_config(self):
        self.broadcast(durak_server.packages.GameConfigPackage.from_GameConfig(self.game_config))

    def lobby_loop(self):
        loop_iteration = 0
        while self.state is GameState.Preperation:
            self.update_player_list()

            config_has_changed = False
            status_has_changed = False
            if self.__dynamic_config and self.__player_count_has_changed:
                config_has_changed = self._update_config()

            # lobby-based game customization here


            # Receiving Player packages
            for player in self.players:
                while received_package := player.read_package():
                    match received_package:
                        case durak_server.packages.StatusUpdatePackage():
                            player.is_ready = received_package.is_ready
                            status_has_changed = True
                        case _:
                            pass  # Logging

            # send config
            if config_has_changed:
                self._send_config()

            # Sending Lobby Status
            if status_has_changed:
                self._send_status_update()

            player_list = [
                {"playername": inner_player.name, "is-ready": inner_player.is_ready}
                for inner_player in self.players]

            all_players_ready = all(player["is-ready"] for player in player_list)
            # Increase iterator if all Players are ready
            if all_players_ready:
                loop_iteration += 1

            if not all_players_ready:
                loop_iteration = 0  # Reset Loop Iteration Counter so waiting for all players restarts

            if all_players_ready and loop_iteration >= 3:
                self.state = GameState.Running


            time.sleep(0.1)

        if self.state == GameState.Running:
            self.init_game()
            self.game_loop()
            


    def init_game(self):
        if not len(self.players):
            self._logger.info("GameSession with 0 players detected.")
            self.state = GameState.Kill
            self.cleanup()
            return

        for player in self.players:
            # Send Game Starting Package to players
            player.send_package(
                durak_server.packages.GameStartPackage()
            )

        self._logger.info(f"Session [{self.code}] switched state to running")


    def game_loop(self):
        scoreboard = {}
        while self.state is GameState.Running:
            
            # Read Player packages
            for player in self.players:
                while received_package := player.read_package():
                    match received_package:
                        case _:
                            pass  # Logging

        if self.state is GameState.Ended:
            self.end_routine()


    def end_routine(self):
        # Send end-routine package

        # Wait for packages to be sent
        time.sleep(0.5)

        self.cleanup()
        self._logger.info(f"Session [{self.code}] ended successfully")

    def add_player(self, player: Player) -> bool:
        """Adds a player to the game session scope. When a player enters the game session scope, player packets will
        be managed by the game session directly. Players can only be added to the scope, while the session is in the
        preperation state.

        Args:
            player (Player): the player to add to the game session scope

        Returns:
            bool: whether the player could be added to the game session scope
        """
        if self.state != GameState.Preperation:
            return False

        self._logger.info(f"{player.name or 'Player'} [{player.client.address}] joined Session [{self.code}]")
        self.players.append(player)
        self._send_status_update()
        self.__player_count_has_changed = True
        config_pkg = durak_server.packages.GameConfigPackage.from_GameConfig(self.game_config)
        player.send_package(durak_server.packages.GameConfigPackage.from_GameConfig(self.game_config))  # send config
        return True

    def cleanup(self):
        """Cleans all resources used by the game session directly
        """
        if self.state == GameState.Cleaned:
            return

        self._logger.info(f"Cleaning up game session {self.code}")
        unregister_game_code(self.code)

        for player in self.players:
            player.client.shutdown()

        self.state = GameState.Cleaned
