import numpy as np


COLORS = np.array(["red", "white", "blue", "green", "yellow"])
# must start at 1, contain at least one of each integer to max
NUMBERS = np.array([1, 1, 1, 2, 2, 3, 3, 4, 4, 5])
MAX_NUMBER = np.max(NUMBERS)
UNIQUE_NUMBERS = np.unique(NUMBERS)
COUNT_NUMBERS = np.bincount(NUMBERS)[1:]
N_COLORS = COLORS.size
N_NUMBERS = NUMBERS.size
N_UNIQUE_NUMBERS = UNIQUE_NUMBERS.size
CARD_NOINFO = np.repeat(COUNT_NUMBERS[:, np.newaxis], N_COLORS, 1)


def color(card):
    return COLORS[color_idx(card)]


def color_idx(card):
    return np.floor(card/N_NUMBERS).astype(int)


def number(card):
    return NUMBERS[np.mod(card, N_NUMBERS).astype(int)]


def number_idx(card):
    return NUMBERS[np.mod(card, N_NUMBERS).astype(int)] - 1


def card2info(card):
    card_info = np.zeros((N_UNIQUE_NUMBERS, N_COLORS))
    card_info[color_idx(card), number_idx(card)] = 1
    return card_info