import numpy as np

COLORS = np.array(["Blue", "Green", "Red", "White", "Yellow"])
COLORS_SHORT = np.array(["b", "g", "r", "w", "y"])
NUMBERS = np.array([1, 1, 1, 2, 2, 3, 3, 4, 4, 5], np.int8)
MAX_NUMBER = np.max(NUMBERS)
UNIQUE_COLORS = np.unique(COLORS)
UNIQUE_NUMBERS = np.unique(NUMBERS)
COUNT_NUMBERS = np.bincount(NUMBERS)[1:].astype(np.int8)
N_COLORS = UNIQUE_COLORS.size
N_NUMBERS = UNIQUE_NUMBERS.size
N_CARDS_PER_NUMBER = COLORS.size
N_CARDS_PER_COLOR = NUMBERS.size
N_CARDS = N_CARDS_PER_COLOR * N_CARDS_PER_NUMBER

CARD_NOINFO = np.repeat(COUNT_NUMBERS[:, np.newaxis], N_COLORS, 1)
CARD_ZEROS = np.zeros((N_NUMBERS, N_COLORS), np.int8)
CARD_ONES = np.ones((N_CARDS_PER_COLOR, N_COLORS), np.int8)

MAX_CLUES = 8
MAX_FUSES = 40


def color_short(card):
    return COLORS_SHORT[color_idx(card)]


def color(card):
    return COLORS[color_idx(card)]


def color_idx(card):
    return np.floor(card/N_CARDS_PER_COLOR).astype(int)


def number(card):
    return NUMBERS[np.mod(card, N_CARDS_PER_COLOR).astype(int)]


def number_idx(card):
    return number(card) - 1


def card2info(card):
    card_info = np.copy(CARD_ZEROS)
    card_info[color_idx(card), number_idx(card)] = 1
    return card_info


def next_player(player_idx, n_players):
    return np.mod(player_idx + 1, n_players)


def player_idx_rel2glob(rel_idx, player_idx, n_players):
    return np.mod(player_idx + 1 + rel_idx, n_players)


def player_idx_glob2rel(glob_idx, player_idx, n_players):
    return np.mod(glob_idx - player_idx, n_players) - 1
