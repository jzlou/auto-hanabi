import util
import numpy as np

CARD_NOINFO = np.repeat(util.COUNT_NUMBERS[:, np.newaxis], util.N_COLORS, 1)
CARD_ZEROS = np.zeros((util.N_CARDS_PER_COLOR, util.N_COLORS), np.int8)
CARD_ONES = np.ones((util.N_CARDS_PER_COLOR, util.N_COLORS), np.int8)


class PlayLeft:
    def __init__(self, n_players, n_handcards):
        self.n_handcards = n_handcards
        self.n_players = n_players
        self.n_fuses = util.MAX_FUSES
        self.n_clues = util.MAX_CLUES
        self.n_undealts = util.N_CARDS
        self.card_infos = np.repeat(CARD_NOINFO[np.newaxis, ...], self.n_handcards, 0)
        self.card_clues = np.repeat(CARD_NOINFO[np.newaxis, ...], self.n_handcards, 0)
        self.card_odds = np.repeat(CARD_ZEROS[np.newaxis, ...], self.n_handcards, 0)
        self.visible_hands = np.repeat(np.repeat(CARD_ZEROS[np.newaxis, np.newaxis, ...], self.n_handcards, 1), self.n_players - 1, 0)
        self.n_cards = np.zeros((self.n_players, ), np.int)
        self.table = np.copy(CARD_ZEROS)
        self.discards = np.copy(CARD_ZEROS)
        return

    def play_turn(self):
        action = ('play', 0)
        return action

    def card_played(self, player_idx, card_idx, card, d_clues, d_fuses):
        return

    def card_discarded(self, player_idx, card_idx, card, d_clues):
        return

    def card_dealt(self, player_idx, card_idx, card):
        return

    def clue_given(self, player_idx, to_player_idx, card_idxs, clue_type, clue_idx):
        return
