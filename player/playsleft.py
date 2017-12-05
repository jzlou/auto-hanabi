import player.clues
import util
import numpy as np


class PlaysLeftPlayer:
    def __init__(self, player_idx, info):
        self.n_heldcards = info.n_heldcards
        self.player_idx = player_idx
        self.last_idx_played = -1
        self.card_infos = np.repeat(util.CARD_NOINFO[np.newaxis, ...], self.n_heldcards, 0)
        return

    def play_turn(self, info):
        # determine card index to play
        card_idx = 0
        action = ('play', (card_idx, ))
        # remove card from hand, shift cards to the left
        self.n_heldcards -= 1
        self.card_infos[card_idx:-1, ...] = self.card_infos[card_idx-1:, ...]
        self.card_infos[-1, ...] = np.zeros((util.UNIQUE_NUMBERS, util.N_COLORS), np.int8)

        self.last_idx_played = card_idx
        return action

    def get_card(self):
        self.card_infos[-1, ...] = util.CARD_NOINFO
        self.n_heldcards += 1
        return 0

    def get_clue(self, card_idxs, clue_hint):
        clue_info = np.zeros((util.UNIQUE_NUMBERS, util.N_COLORS), np.int8)
        if isinstance(clue_hint, str):
            # clue is color clue
            clue_info[:, clue_hint] = 1
        else:
            # clue is number clue
            clue_info[clue_hint, :] = 1
        self.card_infos[card_idxs, ...] *= clue_info
        return

    def get_info(self, info, visible_hands):
        return