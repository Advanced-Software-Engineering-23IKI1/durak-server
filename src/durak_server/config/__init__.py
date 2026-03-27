from durak_server.config.game_config import BasicGameConfig, GameConfig
from durak_server.game.card import CardValue, Deck52, Deck32
from durak_server.config.card_distribution import CARDCOUNT_MAPPING
from durak_server import CONFIG

default_game_config = BasicGameConfig(
    attack_forwarding=bool(CONFIG.get("game", "ATTACK_FORWARDING")),
    attack_forwarding_exact_count_match=bool(CONFIG.get("game", "EXACT_COUNT_MATCH")),
    all_card_defend_early_end=bool(CONFIG.get("game", "DEFEND_EARLY_END")),
    card_order=eval(CONFIG.get("game", "CARD_ORDER")),

    player_card_count=int(CONFIG.get("game", "PLAYER_CARD_COUNT")),
    deck= {"52": Deck52(), "32": Deck32()}[CONFIG.get("game", "DECK_TYPE")]
)
