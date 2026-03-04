from durak_server.config.game_config import BasicGameConfig, GameConfig
from durak_server.game.card import CardValue, Deck52
from durak_server.config.card_distribution import CARDCOUNT_MAPPING

default_game_config = BasicGameConfig(
    attack_forwarding=True,
    attack_forwarding_exact_count_match=False,
    all_card_defend_early_end=False,
    card_order=[
        CardValue.TWO,
        CardValue.THREE,
        CardValue.FOUR,
        CardValue.FIVE,
        CardValue.SIX,
        CardValue.SEVEN,
        CardValue.EIGHT,
        CardValue.NINE,
        CardValue.TEN,
        CardValue.J,
        CardValue.Q,
        CardValue.K,
        CardValue.A,
    ],
    player_card_count = 7,
    deck = Deck52()
)
