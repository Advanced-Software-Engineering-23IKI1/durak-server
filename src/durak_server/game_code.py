from random import choice
from string import ascii_lowercase, digits

use_letters = ascii_lowercase.replace("o", "")
use_letters = use_letters.replace("l", "")
use_digits = digits.replace("0", "")
use_digits = use_digits.replace("1", "")
_GAME_CODE_CHARACTERS = use_letters + use_digits

_USED_GAME_CODES = set()

def generate_game_code() -> str:
    """Generates an unused random 4 letter game code using letters from _GAME_CODE_CHARACTERS

    Returns:
        str: a random game code
    """
    code = ''.join(choice(_GAME_CODE_CHARACTERS) for _ in range(4))

    while code in _USED_GAME_CODES:
        code = ''.join(choice(_GAME_CODE_CHARACTERS) for _ in range(4))

    _USED_GAME_CODES.add(code)
    return code

def unregister_game_code(code: str):
    """Removes a given code from the list of game codes in use

    Args:
        code (str): the game code to remove
    """
    _USED_GAME_CODES.remove(code)
