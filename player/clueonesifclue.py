import player.clues
import util
import numpy as np


class ClueOnesIfClue:
    def __init__(self, player_idx, info):
        self.n_heldcards = info.n_heldcards
        self.player_idx = player_idx
        self.last_idx_played = -1
        self.card_infos = np.repeat(util.CARD_NOINFO[np.newaxis, ...], self.n_heldcards, 0)
        self.card_odds = np.repeat(util.CARD_ZEROS[np.newaxis, ...], self.n_heldcards, 0)
        return

    def play_turn(self, info, visible_hands):
        if info.clues > 0:
            # clue next player where lowest value cards are
            next_player_rel_idx = 0
            clue_hint = np.min(util.number(visible_hands[next_player_rel_idx, ...]))
            clue_type = 'number'
            clue = (next_player_rel_idx, clue_type, clue_hint)
            action = ('clue', clue)
        else:
            # determine card index to play
            playable_cards = self.get_playable_cards(info.table)
            useless_cards = self.get_useless_cards(info)
            odds_playable = np.sum(playable_cards[np.newaxis, ...] * self.card_odds, (2, 1))
            odds_useless = np.sum(useless_cards[np.newaxis, ...] * self.card_odds, (2, 1))
            card_idx = np.argmax(odds_playable)
            action = ('play', (card_idx, ))
            # remove card from hand, shift cards to the left
            self.n_heldcards -= 1
            self.card_infos = np.concatenate((self.card_infos[np.where(np.arange(info.n_heldcards) != card_idx)[0], ...], np.copy(util.CARD_ZEROS)[np.newaxis, ...]), 0)
            self.get_card_odds()

            self.last_idx_played = card_idx
        return action

    def get_card(self):
        self.card_infos[-1, ...] = util.CARD_NOINFO
        self.get_card_odds()
        self.n_heldcards += 1
        return 0

    def get_clue(self, card_idxs, clue_hint):
        clue_info = np.copy(util.CARD_ZEROS)
        if isinstance(clue_hint, str):
            # clue is color clue
            clue_info[:, clue_hint] = 1
        else:
            # clue is number clue
            clue_info[clue_hint - 1, :] = 1
        self.card_infos[card_idxs, ...] *= clue_info
        self.get_card_odds()
        return

    def get_info(self, info, visible_hands):
        self.visible_hands2card_info(visible_hands)
        return

    def get_card_odds(self):
        self.card_odds = self.norm_hand(self.card_infos)
        return

    def norm_hand(self, hand):
        norm = np.sum(hand, (1, 2))[:, np.newaxis, np.newaxis]
        norm[np.where(norm == 0)[0]] = 1
        hand = hand / norm
        return hand

    def get_playable_cards(self, table):
        playable_cards = np.copy(util.CARD_ZEROS)
        for color_idx in range(util.N_COLORS):
            if table[color_idx] < util.N_NUMBERS:
                playable_cards[table[color_idx], color_idx] = 1
        return playable_cards

    def get_discardable_cards(self, info):
        discardable_cards = self.get_useless_cards(info)
        for color_idx in range(util.N_COLORS):
            if info.table[color_idx] < util.N_NUMBERS:
                discardable_cards[info.table[color_idx], color_idx] = 1
        return discardable_cards

    def get_useless_cards(self, info):
        useless_cards = np.copy(util.CARD_ONES)
        max_color_scores = self.get_max_color_scores(info.discards)
        for color_idx in range(util.N_COLORS):
            useless_cards[info.table[color_idx]:max_color_scores[color_idx], color_idx] = 0
        return useless_cards

    def get_max_color_scores(self, discards):
        # TODO figure out when not enough turns to play remaining cards
        cards_left = np.copy(util.CARD_NOINFO) - discards
        max_color_scores = util.MAX_NUMBER * np.ones((util.N_COLORS, ), np.int8)
        for color_idx in range(util.N_COLORS):
            zero_inds = np.where(cards_left[:, color_idx] == 0)[0]
            if zero_inds.size:
                max_color_scores[color_idx] = np.min(zero_inds)
        return max_color_scores

    def visible_hands2card_info(self, visible_hands):
        visible_cards_info = np.copy(util.CARD_ZEROS)
        visible_cards_info[(util.number_idx(visible_hands), util.color_idx(visible_hands))] = 1
        return
