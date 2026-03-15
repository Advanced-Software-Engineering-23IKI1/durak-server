"""High level interactive test client for testing advanced game functions"""

from tests.tcp_test_client import TcpTestClient
import signal
import time
import sys
import os
import pathlib
import enum
from threading import Thread
from typing import Callable, Optional
from queue import Queue

from tests import TEST_CONFIG
from tests.utils.logging import TEST_LOGGER

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout


durak_server_DIR = pathlib.Path(__file__).parent.parent / "src"

sys.path.insert(0, os.path.join(durak_server_DIR))
sys.path.insert(0, os.path.join(pathlib.Path(__file__).parent.parent))

import durak_server
from durak_server.game.card import Card
from durak_server.config import BasicGameConfig


class PlayerRole(enum.Enum):
    PreGame = 0
    Lobby = 1
    Attacker = 2
    Observer = 3
    Defender = 4
    End = -1


class HighLevelInteractiveTestClient(TcpTestClient):

    def __init__(
        self,
        ip,
        port,
        listener_delay: float = 0.5,
        filter_function: Optional[Callable] = None,
    ):
        super().__init__(ip, port)

        self.listener_delay = listener_delay
        self.filter_function = filter_function

        self._role = PlayerRole.PreGame
        self._game_config = None
        self._lobby = []
        self._attack = []

        self._game_code = None
        self._id = None

        self._hand = []
        self._player_hands = []
        self._draw_pile = None
        self._trump = None
        self._player_order = []
        self._table_state = []
        self._player_statuses = []

        self._state_update = False

        self._cmd_queue = Queue()

        self.session = PromptSession()
        self._gamecode = None

        self._dynamic_card_count_caling = None

    def make_interactive(self):

        signal.signal(signal.SIGINT, self._stop)

        self._listener_thread = Thread(target=self._listen_to_packages)
        self._listener_thread.start()

        self._input_thread = Thread(target=self._input_loop)
        self._input_thread.start()

        self.main_loop()

    def _listen_to_packages(self):

        while self._is_running:

            while pkg := self.read_package():

                if self.filter_function:
                    pkg = self.filter_function(pkg)

                if pkg:
                    TEST_LOGGER.debug(pkg)
                    self._update_data(pkg)

            time.sleep(self.listener_delay)

    def _input_loop(self):

        while self._is_running:

            with patch_stdout():
                cmd = self.session.prompt("> ")

            self._cmd_queue.put(cmd)

    def _update_data(self, pkg):

        self._state_update = True

        match pkg:

            case durak_server.packages.LobbyJoinConfirmationPackage():
                self._role = PlayerRole.Lobby
                self._id = pkg.player_id
                print("joined lobby")

            case durak_server.packages.LobbyStatusPackage():
                self._lobby = pkg.players
                self._gamecode = pkg.gamecode

            case durak_server.packages.GameConfigPackage():
                self._game_config = pkg.to_BasicGameConfig()
                self._dynamic_card_count_caling = pkg.dynamic_card_count_scaling

            case durak_server.packages.GameStartPackage():
                self._role = PlayerRole.Observer
                print("GAME STARTED")

            case durak_server.packages.PlayerHandsUpdatePackage():
                self._hand = pkg.hand
                self._player_hands = pkg.player_hands
                self._draw_pile = pkg.draw_pile
                self._trump = pkg.trump
                self._player_order = pkg.player_order

            case durak_server.packages.TableUpdatePackage():
                self._table_state = pkg.table_state

            case durak_server.packages.PlayerStatusPackage():
                self._player_statuses = pkg.statuses
                for status in self._player_statuses:
                    if status.get("player_id") == self._id:
                        if status.get("status") == "attack":
                            self._role = PlayerRole.Attacker
                        elif status.get("status") == "defend":
                            self._role = PlayerRole.Defender
                        elif status.get("status") == "finished":
                            self._role = PlayerRole.End
                        else:
                            self._role = PlayerRole.Observer

            case _:
                pass

    def _handle_command(self, cmd: str):

        cmd = cmd.strip()

        if self._role == PlayerRole.PreGame:
            self._handle_pregame(cmd)

        elif self._role == PlayerRole.Lobby:
            self._handle_lobby(cmd)

        elif self._role in (PlayerRole.Attacker, PlayerRole.Defender, PlayerRole.Observer):
            self._handle_game_command(cmd)

        else:
            print("Unknown state. Valid commands: create/join (pregame), ready/unready/print_lobby_info (lobby), attack/defend/print_game/surrender (in game)")

    def _handle_pregame(self, cmd):

        match cmd.split():

            case ["create", playername]:

                self.send_package(
                    durak_server.packages.StartGameSessionPackage(playername)
                )

            case ["join", gamecode, playername]:

                self.send_package(
                    durak_server.packages.ConnectToGameSessionPackage(
                        gamecode.lower(), playername
                    )
                )

            case _:
                print("Commands:")
                print("create <playername>")
                print("join <gamecode> <playername>")

    def _handle_lobby(self, cmd):

        parts = cmd.split()

        if not parts:
            print("Lobby commands:")
            print("ready")
            print("unready")
            print("print_lobby_info")
            print("set <setting> <value>")
            return

        match parts:

            case ["ready"]:
                self.send_package(
                    durak_server.packages.StatusUpdatePackage(is_ready=True)
                )

            case ["unready"]:
                self.send_package(
                    durak_server.packages.StatusUpdatePackage(is_ready=False)
                )

            case ["print_lobby_info"]:
                self._print_lobby()

            case ["set", setting, value]:
                cfg = self._game_config
                match setting:
                    case "attack_forwarding":
                        attack_forwarding = value.lower() in ("true", "1", "yes", "y")

                        new_cfg = BasicGameConfig(
                            attack_forwarding=attack_forwarding,
                            attack_forwarding_exact_count_match=cfg.attack_forwarding_exact_count_match,
                            all_card_defend_early_end=cfg.all_card_defend_early_end,
                            card_order=cfg.card_order,
                            deck=cfg.deck,
                            player_card_count=cfg.player_card_count,
                        )

                    case "attack_forwarding_exact_count_match":
                        exact = value.lower() in ("true", "1", "yes", "y")

                        new_cfg = BasicGameConfig(
                            attack_forwarding=cfg.attack_forwarding,
                            attack_forwarding_exact_count_match=exact,
                            all_card_defend_early_end=cfg.all_card_defend_early_end,
                            card_order=cfg.card_order,
                            deck=cfg.deck,
                            player_card_count=cfg.player_card_count,
                        )

                    case "all_card_defend_early_end":
                        early_end = value.lower() in ("true", "1", "yes", "y")

                        new_cfg = BasicGameConfig(
                            attack_forwarding=cfg.attack_forwarding,
                            attack_forwarding_exact_count_match=cfg.attack_forwarding_exact_count_match,
                            all_card_defend_early_end=early_end,
                            card_order=cfg.card_order,
                            deck=cfg.deck,
                            player_card_count=cfg.player_card_count,
                        )

                    case "player_card_count":
                        if value == "none":
                            count = None
                            self._dynamic_card_count_caling = True
                        else:
                            value = int(value)
                            self._dynamic_card_count_caling = False

                        new_cfg = BasicGameConfig(
                            attack_forwarding=cfg.attack_forwarding,
                            attack_forwarding_exact_count_match=cfg.attack_forwarding_exact_count_match,
                            all_card_defend_early_end=cfg.all_card_defend_early_end,
                            card_order=cfg.card_order,
                            deck=cfg.deck,
                            player_card_count=count,
                        )
                    case _:
                        print("unknown setting.")
                        return
                self.send_package(
                    durak_server.packages.UserGameConfigPackage.from_GameConfig(
                        new_cfg,
                        dynamic_card_count_scaling=self._dynamic_card_count_caling,
                    )
                )
                print("Config updated.")

            case _:
                print("Lobby commands:")
                print("ready")
                print("unready")
                print("print_lobby_info")
                print("print_game")

    def _format_card(self, card_id: int) -> str:
        if self._game_config:
            for card in self._game_config.deck.cards:
                if card.id == card_id:
                    return str(card)
        return str(card_id)

    def _format_card_list(self, card_ids: list[int]) -> str:
        return ", ".join(self._format_card(card) for card in card_ids)

    def _player_label(self, player_id: int) -> str:
        if self._lobby:
            for player in self._lobby:
                if player.get("player_id") == player_id:
                    return f"{player.get('playername')} ({player_id})"
        return f"Player {player_id}"

    def _print_game(self):
        print("--- GAME STATE ---")
        print(f"Role: {self._role.name}, Player id: {self._id}, Game: {self._gamecode}")
        print(f"Hand ({len(self._hand)}): {self._format_card_list(self._hand)}")
        print(f"Draw pile: {self._draw_pile}, Trump: {self._format_card(self._trump) if self._trump is not None else 'None'}")

        print("Player hand counts:")
        for player_info in self._player_hands:
            player_id = player_info.get("player_id")
            label = self._player_label(player_id)
            print(f"  {label}: {player_info.get('card_count')} cards")

        if self._player_statuses:
            print("Player statuses:")
            for status in self._player_statuses:
                player_id = status.get("player_id")
                label = self._player_label(player_id)
                print(f"  {label}: {status.get('status')}")

        if self._table_state:
            print("Table:")
            for cardpair in self._table_state:
                attack_id = cardpair.get("attack_id")
                defend_id = cardpair.get("defend_id")
                from_player = cardpair.get("from_player")
                from_label = self._player_label(from_player) if from_player is not None else "unknown"
                print(
                    f"  attack_id={attack_id} ({self._format_card(attack_id)}), from={from_label}, defend_id={defend_id} ({self._format_card(defend_id) if defend_id else 'None'})"
                )
        print("---")

    def _handle_attack(self, cmd):
        parts = cmd.split()
        if not parts:
            print("Attack command requires cards, e.g. 'attack 1 5 6'")
            return

        if parts[0] != "attack":
            print("Use 'attack <card_id> [<card_id> ...]'")
            return

        if self._role != PlayerRole.Attacker:
            print("You are not the attacker right now.")
            return

        try:
            cards = [int(card) for card in parts[1:]]
        except ValueError:
            print("Card ids must be integers.")
            return

        if not cards:
            print("You must provide at least one card id to attack.")
            return

        if self._hand and not all(card in self._hand for card in cards):
            print("One or more card ids are not in your current hand.")
            print(f"Current hand: {self._format_card_list(self._hand)}")
            return

        self.send_package(durak_server.packages.PlayerAttackPackage(cards=cards))
        print(f"Sent attack with cards: {self._format_card_list(cards)}")

    def _handle_defense(self, cmd):
        parts = cmd.split()
        if not parts:
            print("Defense command requires pairs, e.g. 'defend attack_id:defend_id ...'")
            return

        if parts[0] != "defend":
            print("Use 'defend attack_id:defend_id [attack_id:defend_id ...]'")
            return

        if self._role != PlayerRole.Defender:
            print("You are not the defender right now.")
            return

        defense_pairs = []
        for pair in parts[1:]:
            if ":" in pair:
                attack_id_str, defend_id_str = pair.split(":", 1)
                try:
                    defense_pairs.append(
                        {"attack_id": int(attack_id_str), "defend_id": int(defend_id_str)}
                    )
                except ValueError:
                    print(f"Invalid pair format: {pair}. Use attack_id:defend_id with integers.")
                    return
            else:
                print(f"Invalid pair format: {pair}. Use attack_id:defend_id.")
                return

        if not defense_pairs:
            print("Provide at least one defense pair.")
            return

        self.send_package(durak_server.packages.PlayerDefensePackage(defense=defense_pairs))
        print(f"Sent defense: {defense_pairs}")

    def _handle_game_command(self, cmd: str):
        parts = cmd.split()
        if not parts:
            print("Game commands:")
            print("attack <card_id> [<card_id> ...]")
            print("defend <attack_id>:<defend_id> [<attack_id>:<defend_id> ...]")
            print("print_game")
            print("surrender")
            return

        if parts[0] == "attack":
            self._handle_attack(cmd)
        elif parts[0] == "defend":
            self._handle_defense(cmd)
        elif parts[0] == "print_game":
            self._print_game()
        elif parts[0] == "surrender":
            self.send_package(durak_server.packages.PlayerSurrenderPackage())
        else:
            print("Game commands:")
            print("attack <card_id> [<card_id> ...]")
            print("defend <attack_id>:<defend_id> [<attack_id>:<defend_id> ...]")
            print("print_game")
            print("surrender")

    def _print_lobby(self):

        if not self._game_config:
            return

        print("--- LOBBY ---")
        print(f"Game {self._gamecode}, Player id: {self._id}")
        print(
            "Config:" + f" Deck: {self._game_config.deck}, "
            f"attack_forwarding: {self._game_config.attack_forwarding} "
            f"(exact count match: {self._game_config.attack_forwarding_exact_count_match})"
        )

        print("Players in lobby:")
        for player in self._lobby:
            print(
                f"  {player['playername']} (id={player['player_id']}): "
                f"{'ready' if player['is-ready'] else 'NOT ready'}"
            )
        print("---")

    def main_loop(self):

        print("High Level Interactive Durak Test Client")

        while self._is_running:

            while not self._cmd_queue.empty():
                cmd = self._cmd_queue.get()
                self._handle_command(cmd)

            if self._state_update:
                if self._role == PlayerRole.Lobby:
                    self._print_lobby()
                elif self._role in (PlayerRole.Attacker, PlayerRole.Defender, PlayerRole.Observer):
                    self._print_game()
                self._state_update = False

            time.sleep(0.05)

    def _stop(self, signum, frame):

        print("Stopping client...")

        self._is_running = False

        try:
            self.session.app.exit()
        except Exception:
            pass

        self._listener_thread.join()
        self._input_thread.join()


def main():

    IP = str(TEST_CONFIG.get("test_server", "IP")).strip()
    PORT = int(TEST_CONFIG.get("test_server", "PORT").strip())

    client = HighLevelInteractiveTestClient(IP, PORT)

    client.make_interactive()


if __name__ == "__main__":
    main()
