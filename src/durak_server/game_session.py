from durak_server.game_state import GameState
from durak_server.game_code import generate_game_code, unregister_game_code
import durak_server.packages
from threading import Thread
from durak_server import Player
from durak_server.server_logging import SessionLogger
import durak_server
import time
import durak_server.config

import durak_server.packages

class GameSession:
    def __init__(self):
        """Generates a new empty game session with a newly generated game code
        """
        self.code = generate_game_code()
        self.players: list[Player] = []
        self.state = GameState.Preperation

        self.game_config = durak_server.config.default_game_config_factory.create_game_config()
        self.end_condition_factory = self.game_config.endcondition_factory


        # Start the game lobby loop
        self.thread = Thread(target=self.lobby_loop)
        self.thread.start()
        self._logger = SessionLogger(gamecode=self.code)

    def update_player_list(self):
        self.players = [player for player in self.players if player.client.is_running]

    def lobby_loop(self):
        loop_iteration = 0
        while self.state is GameState.Preperation:
            self.update_player_list()

            # Receiving Player Ready State
            for player in self.players:
                while received_package := player.read_package():
                    match received_package:
                        case durak_server.packages.StatusUpdatePackage():
                            player.is_ready = received_package.is_ready
                        case _:
                            pass  # Logging

            # Sending Lobby Status
            player_list = [
                {"playername": inner_player.name, "is-ready": inner_player.is_ready}
                for inner_player in self.players]
            for player in self.players:
                player.send_package(
                    durak_server.packages.LobbyStatusPackage(
                        self.code,
                        players=player_list
                    )
                )


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
        
        shop_broadcast_pkg = durak_server.packages.create_ShopBroadcastPackage_from_shop(self.game_config.shop)
        for player in self.players:
            # Send Game Starting Package to players
            player.send_package(
                durak_server.packages.GameStartPackage()
            )
            # Update player values according to game config
            player.currency = self.game_config.base_currency
            player.earn_rate = self.game_config.base_earn_rate
            player._click_modifier = self.game_config.base_modifier
            player.shop = self.game_config.shop()
            player.send_package(shop_broadcast_pkg)

        self._logger.info(f"Session [{self.code}] switched state to running")


        self.end_condition = self.game_config.endcondition_factory.create_EndCondition()
        if isinstance(self.end_condition,durak_server.end_condition.PointBasedEndCondition):
            self.end_condition.add_players(players=self.players)



    def game_loop(self):
        _game_timer_interval = 0.1
        scoreboard = {}
        while self.state is GameState.Running:
            
            # Read Player packages
            for player in self.players:
                while received_package := player.read_package():
                    match received_package:
                        case _:
                            pass  # Logging

            # Check end condition
            if (self.end_condition.is_game_end()):
                self.state = GameState.Ended

            time.sleep(_game_timer_interval)

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
