import player.clues
import util
import numpy as np


class ClueOnesIfClue:
    def __init__(self, player_idx, info):
        self.n_players = info.n_heldcards
        self.n_heldcards = info.n_heldcards
        self.player_idx = player_idx
        self.last_idx_played = -1
        self.card_infos = np.repeat(util.CARD_NOINFO[np.newaxis, ...], self.n_heldcards, 0)
        self.card_clues = np.repeat(util.CARD_NOINFO[np.newaxis, ...], self.n_heldcards, 0)
        self.card_odds = np.repeat(util.CARD_ZEROS[np.newaxis, ...], self.n_heldcards, 0)
        return

    def play_turn(self, info, visible_hands):
        if info.clues > 0:
            # clue next player where lowest value cards are
            player_rel_idx = 0
            clue_hint = np.min(util.number(visible_hands[player_rel_idx, ...]))
            clue_type = 'number'
            card_idxs = np.array([])
            if clue_type is 'color':
                card_idxs = np.where(util.color(visible_hands[player_rel_idx, :]) is clue_hint)[0]
            elif clue_type is 'number':
                card_idxs = np.where(util.number(visible_hands[player_rel_idx, :]) == clue_hint)[0]
            clue = (player_rel_idx, clue_type, clue_hint, card_idxs)
            action = ('clue', clue)
        else:
            # determine card index to play
            playable_cards = get_playable_cards(info.table)
            discardable_cards = get_discardable_cards(info)
            useless_cards = get_useless_cards(info)
            odds_playable = np.sum(playable_cards[np.newaxis, ...] * self.card_odds, (2, 1))
            odds_discardable = np.sum(discardable_cards[np.newaxis, ...] * self.card_odds, (2, 1))
            odds_useless = np.sum(useless_cards[np.newaxis, ...] * self.card_odds, (2, 1))
            if np.max(odds_playable) == 1:
                card_idx = np.argmax(odds_playable)
                action = ('play', (card_idx, ))
                # remove card from hand, shift cards to the left
                self.n_heldcards -= 1
                self.card_infos = np.concatenate((self.card_infos[np.where(np.arange(info.n_heldcards) != card_idx)[0], ...], np.copy(util.CARD_ZEROS)[np.newaxis, ...]), 0)
                self.card_odds = norm_hand(self.card_infos)

                self.last_idx_played = card_idx
            else:
                card_idx = np.argmax(odds_discardable)
                action = ('discard', (card_idx, ))
                # remove card from hand, shift cards to the left
                self.n_heldcards -= 1
                self.card_infos = np.concatenate((self.card_infos[np.where(np.arange(info.n_heldcards) != card_idx)[0], ...], np.copy(util.CARD_ZEROS)[np.newaxis, ...]), 0)
                self.card_odds = norm_hand(self.card_infos)

                self.last_idx_played = card_idx

        return action

    def get_card(self, player_idx, card):
        glob_player_idx = util.player_idx_rel2glob(player_idx, card, self.n_players)
        player_idx = util.player_idx_glob2rel(glob_player_idx, self.player_idx, self.n_players)

        if player_idx == -1:
            self.card_infos[-1, ...] = util.CARD_NOINFO
            self.card_odds = norm_hand(self.card_infos)
            self.n_heldcards += 1

        return

    def get_action(self, action, info):
        if action[0] is 'play' or action[0] is 'discard':
            pass
        elif action[0] is 'clue':
            clue = action[1]
            glob_player_idx = util.player_idx_rel2glob(info.curr_player_idx, clue[0], self.n_players)
            player_idx = util.player_idx_glob2rel(glob_player_idx, self.player_idx, self.n_players)
            clue_type = clue[1]
            clue_hint = clue[2]
            card_idxs = clue[3]

            if player_idx == -1:
                clue_info = np.copy(util.CARD_ZEROS)
                if clue_type is 'color':
                    clue_info[:, clue_hint] = 1
                elif clue_type is 'number':
                    clue_info[clue_hint - 1, :] = 1
                self.card_clues[card_idxs, ...] *= clue_info[np.newaxis, ...]
                self.card_clues[np.logical_not(np.in1d(np.arange(self.n_players), card_idxs)), ...] *= 1 - clue_info[np.newaxis, ...]
                self.card_infos[card_idxs, ...] *= clue_info[np.newaxis, ...]
                self.card_infos[np.logical_not(np.in1d(np.arange(self.n_players), card_idxs)), ...] *= 1 - clue_info[np.newaxis, ...]
                self.card_odds = norm_hand(self.card_infos)
        return


def norm_hand(hand):
    norm = np.sum(hand, (1, 2))[:, np.newaxis, np.newaxis]
    norm[np.where(norm == 0)[0]] = 1
    hand = hand / norm
    return hand


def get_playable_cards(table):
    playable_cards = np.copy(util.CARD_ZEROS)
    for color_idx in range(util.N_COLORS):
        if table[color_idx] < util.N_NUMBERS:
            playable_cards[table[color_idx], color_idx] = 1
    return playable_cards


def get_discardable_cards(info):
    discardable_cards = get_useless_cards(info)
    for color_idx in range(util.N_COLORS):
        if info.table[color_idx] < util.N_NUMBERS:
            discardable_cards[info.table[color_idx], color_idx] = 1
    return discardable_cards


def get_useless_cards(info):
    useless_cards = np.copy(util.CARD_ONES)
    max_color_scores = get_max_color_scores(info.discards)
    for color_idx in range(util.N_COLORS):
        useless_cards[info.table[color_idx]:max_color_scores[color_idx], color_idx] = 0
    return useless_cards


def get_max_color_scores(discards):
    # TODO figure out when not enough turns to play remaining cards
    cards_left = np.copy(util.CARD_NOINFO) - discards
    max_color_scores = util.MAX_NUMBER * np.ones((util.N_COLORS, ), np.int8)
    for color_idx in range(util.N_COLORS):
        zero_inds = np.where(cards_left[:, color_idx] == 0)[0]
        if zero_inds.size:
            max_color_scores[color_idx] = np.min(zero_inds)
    return max_color_scores


def visible_hands2card_info(visible_hands):
    visible_cards_info = np.copy(util.CARD_ZEROS)
    visible_cards_info[(util.number_idx(visible_hands), util.color_idx(visible_hands))] = 1
    return
