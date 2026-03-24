from durak_server.config import GameConfig
from durak_server.player import Player
from durak_server.game.drawpile import DrawPile
from durak_server.game.card import Card
from random import shuffle
import itertools
import time
from durak_server.server_logging import SessionLogger

import durak_server.packages
from durak_server.player import PlayerGameStatus
from durak_server.game_state import GameState


class GameLoop:
    def __init__(
        self, game_config: GameConfig, players: list[Player], logger: SessionLogger
    ):
        self._game_config = game_config
        shuffle(players)
        self._players = players
        self._logger = logger
        self._game_player_list = self._players.copy()  # list of players still in game
        self._leaderboard = []
        self._attack_buffer = []  # list of dicts for the current attack
        # {"attack_card": attacking Card obj, "defend_card": defending Card obj, "from_player": Player obj that attacked}
        self._attack_max = (
            0  # max amount of cards valid for attacking (=initial defender hand count)
        )
        self.draw_list = []
        self._cur_attacker_idx = 0

        self.state = GameState.Running

        self._turn_kill = False  # janky solution for communicating across inner loop recursions on attack forwarding

    @property
    def players(self) -> tuple[Player, ...]:
        return self._players

    def broadcast(self, package):
        for player in self._players:
            player.send_package(package)

    def broadcast_player_hands_update(self):
        for player in self.players:
            player.send_package(
                durak_server.packages.PlayerHandsUpdatePackage(
                    hand=[card.id for card in player.hand],
                    player_hands=[
                        {
                            "player_id": other_player.player_id,
                            "card_count": len(other_player.hand),
                        }
                        for other_player in self._game_player_list
                        if other_player != player
                    ],
                    draw_pile=len(self._drawpile),
                    trump=self._trump_card.id if self._trump_card else None,
                    player_order=[p.player_id for p in self._players],
                )
            )

    def game_start_routine(self):
        self._trump_suit = self._game_config.trump
        deck_cards = [
            card for card_group in self._game_config.cards for card in card_group
        ]
        self._drawpile = DrawPile(deck_cards, self._trump_suit)
        self._trump_card = self._drawpile.trump_card

        # distributing cards to players
        for player in self._players:
            player.hand = self._drawpile.draw(self._game_config.player_card_count)
        self.broadcast_player_hands_update()

    def broadcast_player_status(self):
        self.broadcast(
            durak_server.packages.PlayerStatusPackage(
                statuses=[
                    {"player_id": player.player_id, "status": player.game_status}
                    for player in self._players
                ]
            )
        )

    def get_card_by_id(self, id: int):
        cards = list(itertools.chain(*self._game_config.cards))
        for card in cards:
            if card.id == id:
                return card

    def is_attack_valid(self, target: Player, attacking_cards: list[Card]) -> bool:
        """check whether an attack is valid
        #! does not perform the actual attack!

        Args:
            target (Player): player being attacked
            attacking_cards (list[Card]): list of attacking cards

        Returns:
            bool
        """
        base_msg = f"Attack on {target.name} (id={target.player_id}) using {attacking_cards} failed on"

        # only 1 card type
        if len(set([card.value for card in attacking_cards])) > 1:
            self._logger.debug(base_msg + " unique card type.")
            return False
        # enough cards left for attack
        if self._attack_max > len(attacking_cards) + len(self._attack_buffer):
            self._logger.debug(base_msg + " remaining attack card count.")
            return False
        # card value already attacking or initial attack
        valid_values = []
        for attack in self._attack_buffer:
            valid_values.append(attack["attack_card"].value)
            if attack["defend_card"] is not None:
                valid_values.append(attack["defend_card"].value)
        if not (
            len(self._attack_buffer) == 0 or attacking_cards[0].value in valid_values
        ):
            self._logger.debug(base_msg + " card type present or initial.")
            return False
        return True

    def perform_attack(
        self, origin: Player, target: Player, attacking_cards: list[Card]
    ) -> bool:
        """perform a attack against a player

        Args:
            origin (Player): attacking player
            target (Player): player being attacked
            attacking_cards (list[Card]): list of attacking cards

        Returns:
            bool: success flag
        """
        for card in attacking_cards:
            if card not in origin.hand:
                origin.send_package(
                    durak_server.packages.CardIdNotInPossessionExceptionPackage(card.id)
                )
                return False
        success = True
        for card in attacking_cards:
            if not origin.remove_card(card):
                success = False
            self._attack_buffer.append(
                {"attack_card": card, "defend_card": None, "from_player": origin}
            )
        self._logger.debug(
            f"Attack from {origin.name} (id={origin.player_id}) to {target.name} (id={target.player_id}) with {attacking_cards} was successfull)"
        )
        self.check_players_finished()
        self.update_info()
        return success

    def update_info(self):
        self.broadcast_player_hands_update()
        self.broadcast_table_update()

    def broadcast_table_update(self):
        self.broadcast(
            durak_server.packages.TableUpdatePackage(
                [
                    {
                        "attack_id": attack["attack_card"].id,
                        "from_player": attack["from_player"].player_id,
                        "defend_id": (
                            attack["defend_card"].id if attack["defend_card"] else None
                        ),
                    }
                    for attack in self._attack_buffer
                ]
            )
        )

    def check_players_finished(self):
        for player in self._game_player_list:
            if len(player.hand) == 0:
                if (
                    self._game_config.all_card_defend_early_end
                    and player.game_status == PlayerGameStatus.Defender
                ) or len(self._drawpile) + 1 == 0:
                    player.game_status = PlayerGameStatus.Finished
                    self._leaderboard.append(player)
                    self._game_player_list.remove(player)

    def is_attack_forwarding_possible(self, cards: list[Card], target: Player) -> bool:
        # 1. check basic rules
        if not self._game_config.attack_forwarding:
            return False

        # 2. check value stuff
        if not set(
            [attack["attack_card"].value for attack in self._attack_buffer]
        ) == set([card.value for card in cards]):
            return False
        if self._game_config.attack_forwarding_exact_count_match:
            if not len(self._attack_buffer) == len(cards):
                return False

        # 3. check card limit of next player
        if not len(cards) <= len(target.hand):
            return False
        # if not self.is_attack_valid(
        #     target, [attack["attack_card"] for attack in self._attack_buffer] + cards
        # ):
        #     return False

        return True

    def forward(self, origin: Player, cards: list[Card]):
        for card in cards:
            origin.remove_card(card)
            self._attack_buffer.append(
                {"attack_card": card, "defend_card": None, "from_player": origin}
            )
        self._cur_attacker_idx = (self._cur_attacker_idx + 1) % len(
            self._game_player_list
        )
        self.update_info()
        self.inner_loop()

    def inner_loop(self):
        """inner game loop.
        This function models the game behaviour after the initial attack has been done (all players are attackers)
        """
        designated_defender = self._game_player_list[
            (self._cur_attacker_idx + 1) % len(self._game_player_list)
        ]
        self._logger.debug(
            f"Entered inner attack loop, designated_defender={designated_defender.name} (id={designated_defender.player_id})"
        )
        defend_complete = False
        pickup = False
        defense_started = False
        while (
            self.state == GameState.Running
            and not defend_complete
            and not pickup
            and not self._turn_kill
        ):
            processed_any = False
            for player in self._game_player_list:
                while self.state == GameState.Running:
                    received_package = player.read_package()
                    if received_package is None:
                        break
                    processed_any = True
                    match received_package:
                        case durak_server.packages.PlayerAttackPackage():
                            attack_cards = [
                                self.get_card_by_id(card_int)
                                for card_int in received_package.cards
                            ]
                            if (
                                player == designated_defender
                                and not defense_started
                                and self.is_attack_forwarding_possible(
                                    attack_cards,
                                    self._game_player_list[
                                        (self._cur_attacker_idx + 2)
                                        % len(self._game_player_list)
                                    ],
                                )
                            ):
                                if player not in self.draw_list:
                                    self.draw_list.append(player)
                                self.forward(player, attack_cards)
                            elif player != designated_defender:
                                if not self.is_attack_valid(
                                    designated_defender, attack_cards
                                ):
                                    player.send_package(
                                        durak_server.packages.InvalidAttackExceptionPackage(
                                            "attack invalid"
                                        )
                                    )
                                    continue
                                self.perform_attack(
                                    player, designated_defender, attack_cards
                                )
                                if player not in self.draw_list:
                                    self.draw_list.append(player)

                        case durak_server.packages.PlayerSurrenderPackage():
                            if player == designated_defender:
                                self._logger.debug(
                                    f"Player {player.name} (id={player.player_id}) surrendered"
                                )
                                cards_to_pickup = [
                                    attack["attack_card"]
                                    for attack in self._attack_buffer
                                ] + [
                                    attack["defend_card"]
                                    for attack in self._attack_buffer
                                    if attack["defend_card"] is not None
                                ]
                                designated_defender.hand.extend(cards_to_pickup)
                                self._attack_buffer.clear()
                                self.check_players_finished()
                                self.update_info()
                                pickup = True
                                self._cur_attacker_idx = (
                                    self._cur_attacker_idx + 2
                                ) % len(self._game_player_list)

                        case durak_server.packages.PlayerDefensePackage():
                            if player != designated_defender:
                                continue
                            any_attack_performed = False
                            for cardpair in received_package.defense:
                                attack_card = self.get_card_by_id(cardpair["attack_id"])
                                defense_card = self.get_card_by_id(
                                    cardpair["defend_id"]
                                )
                                if not self.is_defense_valid(attack_card, defense_card):
                                    self._logger.debug(
                                        f"Defending {attack_card} using {defense_card} failed."
                                    )
                                    continue
                                if self.perform_defense(
                                    designated_defender, attack_card, defense_card
                                ):
                                    any_attack_performed = True
                            if any_attack_performed:
                                if designated_defender not in self.draw_list:
                                    self.draw_list.append(designated_defender)
                                player.game_status = PlayerGameStatus.Defender
                                defense_started = True  # forwarding no longer possible
                                defend_complete = self.is_defense_complete()
                                if defend_complete:
                                    self._attack_buffer.clear()
                                    self._cur_attacker_idx = (
                                        self._cur_attacker_idx + 1
                                    ) % len(self._game_player_list)
                                    self.check_players_finished()
                                self.update_info()
            if not processed_any:
                time.sleep(0.05)
        self._turn_kill = True

    def turn(self):
        """game turn
        simulates a game turn (from initial attacker to turn end [drawing cards])
        """
        attacker = None
        for idx, player in enumerate(self._game_player_list):
            if idx == self._cur_attacker_idx:
                player.game_status = PlayerGameStatus.Attacker
                attacker = player
            else:
                player.game_status = PlayerGameStatus.Observer
        designated_defender = self._game_player_list[
            (self._cur_attacker_idx + 1) % len(self._game_player_list)
        ]
        self.broadcast_player_status()
        initial_attack_complete = False
        while self.state == GameState.Running and not initial_attack_complete:
            response = attacker.read_package()
            if response is None:
                time.sleep(0.05)
                continue

            if not isinstance(response, durak_server.packages.PlayerAttackPackage):
                attacker.send_package(
                    durak_server.packages.InvalidAttackExceptionPackage(
                        "attack invalid"
                    )
                )
                continue

            attack_card_list = [
                self.get_card_by_id(card_int) for card_int in response.cards
            ]
            if not self.is_attack_valid(designated_defender, attack_card_list):
                attacker.send_package(
                    durak_server.packages.InvalidAttackExceptionPackage(
                        "attack invalid"
                    )
                )
                continue

            initial_attack_complete = self.perform_attack(
                attacker, designated_defender, attacking_cards=attack_card_list
            )

        if self.state != GameState.Running:
            return

        self.draw_list.append(attacker)

        for player in self._game_player_list:
            player.game_status = PlayerGameStatus.Attacker
        self.broadcast_player_status()
        self._turn_kill = False
        self.inner_loop()
        self._logger.debug("Turn finished.")

    def _get_cardgroup_idx(self, s_card: Card) -> int:
        for idx, cardgroup in enumerate(self._game_config.cards):
            for card in cardgroup:
                if card == s_card:
                    return idx
        return None

    def is_defense_valid(self, attack_card: Card, defend_card: Card) -> bool:
        return self._get_cardgroup_idx(attack_card) < self._get_cardgroup_idx(
            defend_card
        )

    def perform_defense(
        self, defender: Player, attack_card: Card, defend_card: Card
    ) -> bool:
        for attack in self._attack_buffer:
            if attack["attack_card"] == attack_card:
                if (
                    attack["defend_card"] is not None
                ):  # prevent defending a card multiple times
                    return False
                attack["defend_card"] = defend_card
        success = defender.remove_card(defend_card)
        self.check_players_finished()
        return True

    def is_defense_complete(self) -> bool:
        return all(
            [attack["defend_card"] is not None for attack in self._attack_buffer]
        )

    def redraw(self):
        for player in self.draw_list:
            if len(player.hand) < self._game_config.player_card_count:
                player.hand = player.hand + self._drawpile.draw(
                    self._game_config.player_card_count - len(player.hand)
                )
        self.check_players_finished()
        self.update_info()

    def loop(self):
        while self.state == GameState.Running:
            self.turn()
            self.redraw()
