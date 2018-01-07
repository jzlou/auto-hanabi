import util
import numpy as np


class PlayLeft:
    def __init__(self, n_players, n_handcards):
        self.n_handcards = n_handcards
        self.n_players = n_players
        self.curr_player_idx = None
        self.n_fuses = util.MAX_FUSES
        self.n_clues = util.MAX_CLUES
        self.n_undealts = util.N_CARDS
        self.card_infos = np.repeat(util.CARD_NOINFO[np.newaxis, ...], self.n_handcards, 0)
        self.card_clues = np.repeat(util.CARD_NOINFO[np.newaxis, ...], self.n_handcards, 0)
        self.card_odds = np.repeat(util.CARD_ZEROS[np.newaxis, ...], self.n_handcards, 0)
        self.visible_hands = np.repeat(np.repeat(util.CARD_ZEROS[np.newaxis, np.newaxis, ...], self.n_handcards, 1), self.n_players - 1, 0)
        self.n_cards = np.zeros((self.n_players, ), np.int)
        self.table = np.copy(util.CARD_ZEROS)
        self.discards = np.copy(util.CARD_ZEROS)
        return

    def start_game(self, first_player_idx):
        r"""Get player ready for the game to start.

        Once provided `first_player_idx`, initialize all internal data in preparation for first turn.

        Parameters
        ----------
        first_player_idx : int
            Index of the first player, clockwise relative to self.

        """
        self.curr_player_idx = first_player_idx
        return

    def play_turn(self):
        r"""Play a turn by telling game object your action.

        Player chooses what action to take and on what cards or what clue to give to whom. Main logic for a player
        ruleset.

        Returns
        ----------
        action : tuple
            Action tuple, where first element is string description {'play', 'discard', 'clue'} and second element is
            action metadata. If 'play' or 'discard', second element is card index. If 'clue', second element is a tuple
            itself of (clue_type, clue_hint, card_idxs).

        """
        action = ('play', -1)
        return action

    def invalid_card_played(self, player_idx, card_idx, card, n_fuses):
        return

    def valid_card_played(self, player_idx, card_idx, card, n_clues):
        return

    def card_discarded(self, player_idx, card_idx, card, n_clues):
        return

    def clue_given(self, player_idx, to_player_idx, card_idxs, clue_type, clue_idx):
        return

    def card_dealt(self, player_idx, card_idx, card):
        return

