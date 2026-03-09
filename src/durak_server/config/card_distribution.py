# configs for setting up card distributiond depending on player count, hard-coded for now

from durak_server.game.card import Deck32, Deck52

DECK32_MAPPING = {
    1: 10,
    2: 8,
    3: 7,
    4: 5,
    5: 4,
    6: 4,
    7: 3,
    8: 3,
}


DECK52_MAPPING = {
    1: 20,
    2: 12,
    3: 8,
    4: 8,
    5: 7,
    6: 6,
    7: 6,
    8: 5,
    9: 4,
    10: 4,
}


CARDCOUNT_MAPPING = {
    Deck32(): DECK32_MAPPING,
    Deck52(): DECK52_MAPPING,
}
