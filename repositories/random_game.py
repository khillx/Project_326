# python file that will generate a random game from a list of app ids
# relies on steam_game_info.py to get game info based on app id

import random
from steam_game_info import get_steam_game_info

# Example Steam AppIDs for demo
GAME_IDS = []

def load_game_ids(filename="games.txt"):
    game_ids = []
    with open(filename, "r") as f:
        for line in f:
            game_ids.append(int(line))
    return game_ids

GAME_IDS = load_game_ids()

def get_random_game():
    appid = random.choice(GAME_IDS)
    return get_steam_game_info(appid)

