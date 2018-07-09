import player.clues
from util import CARD_ZEROS, CARD_ONES, CARD_NOINFO
import util
import numpy as np
import disp
# TODO remove logging as it is kinda 'cheating'
import logging


class ClueKeying:
    def __init__(self, n_players, n_handcards):
        r"""Initialize a player.

        Initialize all internal fields and prepare player object for gameplay.

        Parameters
        ----------
        n_players : int
            Total number of players.
        n_handcards : int
            Number of cards in each players hand (before last round).

        """
        self.n_handcards = n_handcards
        self.n_players = n_players
        handcards_info_size = (self.n_players, self.n_handcards, 1, 1)
        self.curr_player_idx = None
        self.n_fuses = util.MAX_FUSES
        self.n_clues = util.MAX_CLUES
        self.n_undealt = util.N_CARDS
        self.hands = np.tile(CARD_ZEROS[np.newaxis, np.newaxis, ...], handcards_info_size)
        self.clues_hands = np.tile(CARD_ONES[np.newaxis, np.newaxis, ...], handcards_info_size)
        self.info_hands = np.tile(CARD_ONES[np.newaxis, np.newaxis, ...], handcards_info_size)
        self.odds_hands = np.tile(CARD_ZEROS[np.newaxis, np.newaxis, ...], handcards_info_size)
        self.n_cards = np.zeros((self.n_players, ), np.int)
        self.table = np.copy(CARD_ZEROS)
        self.discards = np.copy(CARD_ZEROS)
        self.last_cluegiver = -1
        self.last_clue = -np.ones((4, 1))
        self.own_hand_odds = np.tile(CARD_ZEROS[np.newaxis, ...], (self.n_handcards, 1, 1)).astype(np.float)
        self.self_unaccounted_cards = CARD_NOINFO
        # self.hand_odds = np.tile(CARD_ZEROS[np.newaxis, np.newaxis, ...], handcards_info_size).astype(np.float)
        # self.unaccounted_cards = np.tile(CARD_NOINFO[np.newaxis, np.newaxis, ...], handcards_info_size).astype(np.float)

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

        # determine action to take
        valid_action = False

        #if person to your right gave last clue or no clues left
        if (self.last_cluegiver == self.n_players - 2 or not self.n_clues):
            # follow last clue instruction
            possible_clues = self.get_possible_clues(self.last_clue[0], -1)
            cluable_player_idxs = self.exclude_idxs(np.array([self.last_clue[0], -1]))
            action = decode_clue(possible_clues, self.last_clue, cluable_player_idxs)

        else:

            # for cluing person to your left
            possible_clues = self.get_possible_clues(-1, 0)

            if self.n_clues > 1:
                # if you know an action for sure, do it
                odds_playable = np.sum(get_playable_cards(self.table)*self.own_hand_odds, (1, 2))
                odds_discardable = np.sum(get_discardable_cards(self.table)*self.own_hand_odds, (1, 2))
                odds_useless = np.sum(get_useless_cards(self.table, self.discards)*self.own_hand_odds, (1, 2))

                PLAY_THRESH = 1
                DISCARD_THRESH = 1
                USELESS_THRESH = 1
                if np.any(odds_playable >= PLAY_THRESH):
                    action = ('play', np.where(odds_playable >= PLAY_THRESH)[0][0])
                    valid_action = True
                elif np.any(odds_discardable >= DISCARD_THRESH):
                    action = ('discard', np.where(odds_discardable >= DISCARD_THRESH)[0][0])
                    valid_action = True
                elif np.any(odds_useless >= USELESS_THRESH):
                    action = ('discard', np.where(odds_useless >= USELESS_THRESH)[0][0])
                    valid_action = True
                else:
                    # get person to your left to play a card
                    rank_to_play_0 = self.get_playability_rank_to_play(0)

                    if not rank_to_play_0 == -1:
                        clue_info = ('play', rank_to_play_0)
                        logging.info('Trying to get player to my left to play {} most playable card'.format(rank_to_play_0))
                        clue = encode_clue(possible_clues, clue_info, self.exclude_idxs(np.array([0, -1])))
                        if not clue[0] == -1:
                            clue_idxs = np.where(np.sum(self.hands[clue[0], ...], axis=(2 - clue[1]))[:, clue[2]])[0]
                            action = ('clue', (clue[0], 'color' if clue[1] else 'number', clue[2], clue_idxs))
                            valid_action = True


            # if no playable cards or only one clue left
            if self.n_clues == 1 or not valid_action:

                # TODO tell to play if next person's communal top discardable card (after clue given? could be impossible, will have to check) is discardable

                rank_to_discard_0 = self.get_discardability_rank_to_discard(0)

                if not rank_to_discard_0 == -1:
                    clue_info = ('discard', rank_to_discard_0)
                    logging.info('Trying to get player to my left to discard {} most discardable card'.format(rank_to_discard_0))
                    clue = encode_clue(possible_clues, clue_info, self.exclude_idxs(np.array([0, -1])))
                    if not clue[0] == -1:
                        clue_idxs = np.where(np.sum(self.hands[clue[0], ...], axis=(2 - clue[1]))[:, clue[2]])[0]
                        action = ('clue', (clue[0], 'color' if clue[1] else 'number', clue[2], clue_idxs))
                        valid_action = True

            if not valid_action:
                # this only happens if no discardable cards in their hand
                odds_discardable = np.sum(get_discardable_cards(self.table)*self.own_hand_odds, (1, 2))

                action = ('discard', np.argmax(odds_discardable))

        return action

    def invalid_card_played(self, player_idx, card_idx, card, n_fuses):
        r"""Learn that an unplayable card was played.

        Even when this player's card was played, the game lets all players know of an invalid play.

        Parameters
        ----------
        player_idx : int
            Relative index of the player who played the card.
        card_idx : int
            Index of the card played in the players hand.
        card : int
            Card index of the played card.
        n_fuses : int
            Number of fuses remaining after card was played.

        """
        self.discards += util.card2info(card)
        self.n_fuses = n_fuses
        self.reduce_hand(player_idx, card_idx)
        if player_idx == -1:
            self.self_unaccounted_cards = CARD_NOINFO - (self.table + self.discards + np.sum(self.hands[0:-1], (0, 1)) + np.sum(self.own_hand_odds, 0))
            reweight = np.maximum(self.self_unaccounted_cards - util.card2info(card), 0) / np.maximum(self.self_unaccounted_cards, 1)
            self.own_hand_odds *= reweight
            self.own_hand_odds = norm_hand(self.own_hand_odds)
        return

    def valid_card_played(self, player_idx, card_idx, card, n_clues):
        r"""Learn that a playable card was played.

        Even when this player's card was played, the game lets all players know of a valid play.

        Parameters
        ----------
        player_idx : int
            Relative index of the player who played the card.
        card_idx : int
            Index of the card played in the players hand.
        card : int
            Card index of the played card.
        n_clues : int
            Number of clues remaining after card was played.

        """
        self.table += util.card2info(card)
        self.n_clues = n_clues
        self.reduce_hand(player_idx, card_idx)
        if player_idx == -1:
            self.self_unaccounted_cards = CARD_NOINFO - (self.table + self.discards + np.sum(self.hands[0:-1], (0, 1)) + np.sum(self.own_hand_odds, 0))
            reweight = np.maximum(self.self_unaccounted_cards - util.card2info(card), 0) / np.maximum(self.self_unaccounted_cards, 1)
            self.own_hand_odds *= reweight
            self.own_hand_odds = norm_hand(self.own_hand_odds)
        return

    def card_discarded(self, player_idx, card_idx, card, n_clues):
        r"""Learn that a card was discarded.

        Even when this player's card was discarded, the game lets all players know of a discard.

        Parameters
        ----------
        player_idx : int
            Relative index of the player who discarded the card.
        card_idx : int
            Index of the card discarded in the players hand.
        card : int
            Card index of the discarded card.
        n_clues : int
            Number of clues remaining after card was discarded.

        """
        self.discards += util.card2info(card)
        self.n_clues = n_clues
        self.reduce_hand(player_idx, card_idx)
        if player_idx == -1:
            self.self_unaccounted_cards = CARD_NOINFO - (self.table + self.discards + np.sum(self.hands[0:-1], (0, 1)) + np.sum(self.own_hand_odds, 0))
            reweight = np.maximum(self.self_unaccounted_cards - util.card2info(card), 0) / np.maximum(self.self_unaccounted_cards, 1)
            self.own_hand_odds *= reweight
            self.own_hand_odds = norm_hand(self.own_hand_odds)
        return

    def clue_given(self, player_idx, to_player_idx, card_idxs, clue_type, clue_idx):
        r"""Learn that a clue was given.

        Even when this player is giving the clue, the game lets all players know of a clue.

        Parameters
        ----------
        player_idx : int
            Relative index of the player who gave the clue.
        to_player_idx : int
            Relative index of the player who received the clue.
        card_idxs : array of int
            Hand indexes of the cards being informed about.
        clue_type : {'number', 'color'}
            Type of clue given.
        clue_idx : int
            Index for given clue type.

        """
        self.n_clues -= 1
        self.last_cluegiver = player_idx
        self.last_clue[0] = player_idx
        self.last_clue[1] = to_player_idx
        self.last_clue[2] = [1 if clue_type is 'color' else 0]
        self.last_clue[3] = clue_idx

        if clue_type is 'number':
            for card_idx in range(self.n_cards[to_player_idx]):
                if np.isin(card_idx, card_idxs):
                    self.clues_hands[to_player_idx, card_idx, ...] *= get_number_clue_mask(clue_idx)
                else:
                    self.clues_hands[to_player_idx, card_idx, ...] *= get_number_nonclue_mask(clue_idx)
        elif clue_type is 'color':
            for card_idx in range(self.n_cards[to_player_idx]):
                if np.isin(card_idx, card_idxs):
                    self.clues_hands[to_player_idx, card_idx, ...] *= get_color_clue_mask(clue_idx)
                else:
                    self.clues_hands[to_player_idx, card_idx, ...] *= get_color_nonclue_mask(clue_idx)

        return

    def card_dealt(self, player_idx, card, n_cards):
        r"""Learn that a card was dealt.

        Even when this player is dealt a card, the game lets all players know of a deal. Card is always dealt to the
        right-most position, with all other cards shifting left.

        Parameters
        ----------
        player_idx : int
            Relative index of the player who was dealt a card.
        card : int or empty
            Card index of the dealt card, or empty if this player got the new card.
        n_cards : int
            Number of cards in receiving player's hand after card was dealt.

        """
        self.n_cards[player_idx] += 1
        assert (self.n_cards[player_idx] == n_cards)
        if player_idx == -1 or player_idx == self.n_players:
            self.hands[player_idx][self.n_cards[player_idx] - 1, ...] = CARD_NOINFO
        else:
            card_info = util.card2info(card)
            self.hands[player_idx][self.n_cards[player_idx] - 1, ...] = card_info
            self.hands[-1][:self.n_cards[player_idx], ...] -= card_info

        if player_idx == -1:
            self.self_unaccounted_cards = CARD_NOINFO - (self.table + self.discards + np.sum(self.hands[0:-1], (0, 1)) + np.sum(self.own_hand_odds[:self.n_cards[-1]], 0))
            self.own_hand_odds[self.n_cards[player_idx] - 1] = self.self_unaccounted_cards
            self.own_hand_odds = norm_hand(self.own_hand_odds)
        else:
            self.self_unaccounted_cards = CARD_NOINFO - (self.table + self.discards + np.sum(self.hands[0:-1], (0, 1)) + np.sum(self.own_hand_odds, 0))
            reweight = np.maximum(self.self_unaccounted_cards - util.card2info(card), 0) / np.maximum(self.self_unaccounted_cards, 1)
            self.own_hand_odds *= reweight
            self.own_hand_odds = norm_hand(self.own_hand_odds)
        return

    def reduce_hand(self, player_idx, card_idx):
        keep_inds = np.where(np.arange(self.n_cards[player_idx]) != card_idx)[0]
        self.n_cards[player_idx] -= 1
        self.hands[player_idx][:self.n_cards[player_idx], ...] = self.hands[player_idx][keep_inds, ...]
        self.hands[player_idx][self.n_cards[player_idx], ...] = CARD_ZEROS
        self.clues_hands[player_idx][:self.n_cards[player_idx], ...] = self.clues_hands[player_idx][keep_inds, ...]
        self.clues_hands[player_idx][self.n_cards[player_idx], ...] = CARD_ONES
        if player_idx == -1:
            self.own_hand_odds[:self.n_cards[player_idx], ...] = self.own_hand_odds[keep_inds, ...]
        return

    def get_discardability_rank_to_discard(self, player_idx):
        return self.get_doability_rank_to_do(player_idx, get_discardable_cards(self.table))

    def get_playability_rank_to_play(self, player_idx):
        return self.get_doability_rank_to_do(player_idx, get_playable_cards(self.table))

    def get_doability_rank_to_do(self, player_idx, doable_cards):

        # TODO this should be more complicated, involving joint playability, not just based on clues

        hand_odds = norm_hand(CARD_NOINFO*self.clues_hands[player_idx, ...])
        odds_doable = np.sum(doable_cards[np.newaxis, ...] * hand_odds, (2, 1))
        ranked_doability = np.argsort(-odds_doable)
        # determine which card indices are actually doable
        actual_doable = np.any(doable_cards * self.hands[player_idx], (1, 2))
        # get joint-playability-ranked order of actually playable card indices
        top_doable_idx = np.where(actual_doable[ranked_doability])[0]
        if not top_doable_idx.size:
            return -1

        return top_doable_idx[0]

    def get_possible_clues(self, clue_from, clue_to):
        communal_idxs = np.array([clue_from, clue_to])
        # get indices of visible hands, ordered left to right from clue giver
        hand_idxs = np.delete(np.arange(0, self.n_players), np.mod(communal_idxs, self.n_players))
        hand_idxs = (np.mod(np.sort(np.mod(hand_idxs - clue_from, self.n_players)) + clue_from, self.n_players)).astype(np.uint)
        hands = self.hands[hand_idxs]
        possible_color_clues = np.any(hands, (1, 2))
        possible_number_clues = np.any(hands, (1, 3))
        # disp.hand2string_basic(util.hand2cards(hands[0, :]))
        possible_clues = np.where(np.concatenate(
            (np.reshape(possible_number_clues, (possible_number_clues.shape[0], 1, possible_number_clues.shape[1])),
             np.reshape(possible_color_clues,
                        (possible_color_clues.shape[0], 1, possible_color_clues.shape[1]))), 1))

        # possible clues are in form (relative player_idx, number (0) or color (1), color/number idx)
        return possible_clues

    def exclude_idxs(self, idxs):
        return np.delete(np.arange(0, self.n_players), np.mod(idxs, self.n_players))


def cards_possible(table, discards, hands):
    return CARD_NOINFO - table - discards - np.sum(hands, axis=(0, 1))


def norm_hand(hand):
    norm = np.sum(hand, (1, 2))[:, np.newaxis, np.newaxis]
    norm[np.where(norm == 0)[0]] = 1
    hand = hand / norm
    return hand


def get_playable_cards(table):
    playable_cards = np.concatenate((np.copy(CARD_ZEROS), np.zeros((1, table.shape[1]))), 0)
    playable_cards[np.sum(table, axis=0), np.arange(util.N_COLORS)] = 1
    return playable_cards[:-1, :]


def get_discardable_cards(visible_cards):
    discardable_cards = (np.copy(CARD_NOINFO) - visible_cards) != 1
    return discardable_cards


def get_useless_cards(table, discards):
    useless_cards = np.copy(CARD_ONES)
    max_color_scores = get_max_color_scores(discards)
    for color_idx in range(util.N_COLORS):
        useless_cards[np.sum(table[:, color_idx]):max_color_scores[color_idx], color_idx] = 0
    useless_cards[0, :] = 0
    return useless_cards


def get_max_color_scores(discards):
    # TODO figure out when not enough turns to play remaining cards
    cards_left = np.copy(CARD_NOINFO) - discards
    max_color_scores = util.MAX_NUMBER * np.ones((util.N_COLORS,), np.int8)
    for color_idx in range(util.N_COLORS):
        zero_inds = np.where(cards_left[:, color_idx] == 0)[0]
        if zero_inds.size:
            max_color_scores[color_idx] = np.min(zero_inds)
    return max_color_scores


def get_color_clue_mask(color_idx):
    mask = np.copy(CARD_ZEROS)
    mask[:, color_idx] = 1
    return mask


def get_number_clue_mask(number_idx):
    mask = np.copy(CARD_ZEROS)
    mask[number_idx, :] = 1
    return mask


def get_color_nonclue_mask(color_idx):
    return 1 - get_color_clue_mask(color_idx)


def get_number_nonclue_mask(number_idx):
    return 1 - get_number_clue_mask(number_idx)


def encode_clue(possible_clues, clue_info, clueable_player_idxs):

    logging.info(clue_info)
    if clue_info[0] == 'play':
        poss_idx = 2*clue_info[1]
    else:
        poss_idx = 2*clue_info[1] + 1


    logging.debug('{}'.format(possible_clues))

    logging.info('Using poss_idx of {}'.format(poss_idx))

    if poss_idx >= possible_clues[0].size:
        clue = np.array([-1, -1, -1])
        return clue

    player_idx = clueable_player_idxs[possible_clues[0][poss_idx]]
    clue_type = possible_clues[1][poss_idx]
    clue_idx = possible_clues[2][poss_idx]
    clue = np.array([player_idx, clue_type, clue_idx])

    return clue


def decode_clue(possible_clues, clue_info, clueable_player_idxs):

    rel_clue_idx = np.where(clueable_player_idxs == clue_info[1])[0][0]
    poss_player_match = np.where(possible_clues[0] == rel_clue_idx)[0]
    poss_type_match = np.where(possible_clues[1] == clue_info[2])[0]
    poss_clue_match = np.where(possible_clues[2] == clue_info[3])[0]
    poss_idx = np.intersect1d(poss_player_match, np.intersect1d(poss_type_match, poss_clue_match))[0]

    logging.debug('{}'.format(possible_clues))
    logging.info('Received poss_idx of {}'.format(poss_idx))

    action_type = 'play' if not np.mod(poss_idx, 2) else 'discard'
    logging.info(action_type)
    card_idx = np.floor(poss_idx/2).astype(np.int)

    action = (action_type, card_idx)


    return action


def odds_sans_players(hands, clues, table, discards, visible_hands):
    return
