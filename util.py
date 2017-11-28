import numpy as np


COLORS = np.array(["red", "white", "blue", "green", "yellow"])
NUMBERS = np.array([1, 1, 1, 2, 2, 3, 3, 4, 4, 5])


def color(card):
    return COLORS[color_idx(card)]


def color_idx(card):
    return np.floor(card/10).astype(int)


def number(card):
    return NUMBERS[number_idx(card)]


def number_idx(card):
    return np.mod(card, 10).astype(int)
