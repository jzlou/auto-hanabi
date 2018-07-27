import player.clues
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
        self.n_players = n_players
        self.curr_player_idx = None
        self.n_fuses = util.MAX_FUSES
        self.n_clues = util.MAX_CLUES
        self.n_undealt = util.N_CARDS
        self.hands = np.tile(util.CARD_ZEROS[np.newaxis, np.newaxis, ...], (self.n_players, n_handcards, 1, 1))
        self.clues_hands = np.tile(util.CARD_ONES[np.newaxis, np.newaxis, ...],
                                   (self.n_players, n_handcards, 1, 1))
        self.info_hands = np.tile(util.CARD_ZEROS[np.newaxis, np.newaxis, ...],
                                  (self.n_players, n_handcards, 1, 1))
        self.odds_hands = np.tile(util.CARD_ZEROS[np.newaxis, np.newaxis, ...],
                                  (self.n_players, n_handcards, 1, 1))
        self.n_cards = np.zeros((self.n_players,), np.int)
        self.table = np.copy(util.CARD_ZEROS)
        self.discards = np.copy(util.CARD_ZEROS)
        self.last_cluegiver = -1
        self.last_clue = -np.ones((4, 1))
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
            top_playable = np.array([])

            # for cluing person to your left
            possible_clues = self.get_possible_clues(-1, 0)

            if self.n_clues > 1:
                # get person to your left to play a card
                ranked_playability_0 = self.rank_playability(0)
                actual_playable_0 = np.any(get_playable_cards(self.table)*self.hands[0], (1, 2))
                top_playable_0 = np.where(actual_playable_0[ranked_playability_0])[0]

                if top_playable_0.size:
                    rank_to_play_0 = np.where(ranked_playability_0 == top_playable_0[0])[0]
                    clue_info = ('play', rank_to_play_0[0])
                    logging.info('Trying to get player to my left to play {} most playable card, card {}'.format(rank_to_play_0[0], ranked_playability_0[rank_to_play_0[0]]))
                    clue = encode_clue(possible_clues, clue_info, self.exclude_idxs(np.array([0, -1])))
                    valid_action = True

            # if no playable cards or only one clue left
            if self.n_clues == 1 or not valid_action:

                # TODO tell to play if next person's communal top discardable card (after clue given? could be impossible, will have to check) is discardable

                ranked_discardability_0 = self.rank_discardability(0, np.array([0, -1]))
                actual_discardable_0 = np.any(get_discardable_cards(self.table)*self.hands[0], (1, 2))
                top_discardable_0 = np.where(actual_discardable_0[ranked_discardability_0])[0]
                if top_discardable_0.size:
                    rank_to_discard_0 = np.where(ranked_discardability_0 == top_discardable_0[0])[0]
                    clue_info = ('discard', rank_to_discard_0[0])
                    logging.info('Trying to get player to my left to discard {} most discardable card, card {}'.format(rank_to_discard_0[0], ranked_discardability_0[rank_to_discard_0[0]]))
                    clue = encode_clue(possible_clues, clue_info, self.exclude_idxs(np.array([0, -1])))
                    valid_action = True

            if valid_action:
                if not clue[1]:
                    # number
                    clue_idxs = np.where(np.sum(self.hands[clue[0], ...], axis=2)[:, clue[2]])[0]
                else:
                    # color
                    clue_idxs = np.where(np.sum(self.hands[clue[0], ...], axis=1)[:, clue[2]])[0]

                action = ('clue', (clue[0], 'color' if clue[1] else 'number', clue[2], clue_idxs))
            else:
                # this only happens if no discardable cards in their hand
                action = ('discard', 0)

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
            self.hands[player_idx][self.n_cards[player_idx] - 1, ...] = util.CARD_NOINFO
        else:
            card_info = util.card2info(card)
            self.hands[player_idx][self.n_cards[player_idx] - 1, ...] = card_info
            self.hands[-1][:self.n_cards[player_idx], ...] -= card_info

        return

    def reduce_hand(self, player_idx, card_idx):
        keep_inds = np.where(np.arange(self.n_cards[player_idx]) != card_idx)[0]
        self.n_cards[player_idx] -= 1
        self.hands[player_idx][:self.n_cards[player_idx], ...] = self.hands[player_idx][keep_inds, ...]
        self.hands[player_idx][self.n_cards[player_idx], ...] = util.CARD_ZEROS
        self.clues_hands[player_idx][:self.n_cards[player_idx], ...] = self.clues_hands[player_idx][keep_inds, ...]
        self.clues_hands[player_idx][self.n_cards[player_idx], ...] = util.CARD_ONES
        return

    def rank_discardability(self, , visible_hands):

        # get indices of visible hands
        hand_idxs = np.delete(np.arange(0, self.n_players), np.mod(communal_idxs, self.n_players))
        # all visible cards to communal players
        visible_cards = self.table + self.discards + np.sum(self.hands[hand_idxs], (0, 1))
        discardable_cards = get_discardable_cards(visible_cards)
        hand_odds = norm_hand(util.CARD_NOINFO*self.clues_hands[player_idx, ...])
        odds_discardable = np.sum(discardable_cards[np.newaxis, ...] * hand_odds, (2, 1))

        return np.argsort(odds_discardable)

    def rank_playability(self, player_idx):

        playable_cards = get_playable_cards(self.table)
        hand_odds = norm_hand(util.CARD_NOINFO*self.clues_hands[player_idx, ...])
        odds_playable = np.sum(playable_cards[np.newaxis, ...] * hand_odds, (2, 1))

        return np.argsort(odds_playable)

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

    def order_hands(from_idx, to_idx, n_players):
        hand_idxs = np.arange(n_players)
        remaining_idxs = np.delete(hand_idxs, np.mod(hand_idxs, n_players))
        ordered_idxs = (np.mod(np.sort(np.mod(remaining_idxs - from_idx, n_players)) + from_idx, n_players)).astype(
            np.uint)
        return ordered_idxs

    def exclude_order_hands(self, exclude_idxs):
        hand_idxs = exclude_order_idxs(exclude_idxs, self.n_players)
        return self.hands[hand_idxs]


def card_probs_from_clues(card_clues, visible_cards):
    n_cards = card_clues.shape[0]
    unknown_card = util.CARD_NOINFO - np.sum(visible_cards, 0)
    card_probs = np.tile(unknown_card[np.newaxis, ...], (n_cards, 1, 1))
    # I think this relies on the fact that clues apply to all held cards, whether positive or negative
    # so this only works if card_info is from valid clues, not inferred or otherwise learned info
    for ii in range(n_cards):
        card_probs[ii] = norm_card(unknown_card*card_clues[ii])
        unknown_card -= card_probs[ii]
    return card_probs


def rank_discardability(hand_info, visible_cards):

    # get indices of visible hands
    hand_idxs = np.delete(np.arange(0, self.n_players), np.mod(communal_idxs, self.n_players))
    # all visible cards to communal players
    visible_cards = self.table + self.discards + np.sum(self.hands[hand_idxs], (0, 1))
    discardable_cards = get_discardable_cards(visible_cards)
    hand_odds = norm_hand(util.CARD_NOINFO*self.clues_hands[player_idx, ...])
    odds_discardable = np.sum(discardable_cards[np.newaxis, ...] * hand_odds, (2, 1))

    return np.argsort(odds_discardable)

def exclude_order_idxs(exclude_idxs, n_idxs):
    r"""Order a set of indices with exclusions.

    First exclude index is used as the "base" for ordering purposes. Results is indices [0 N) excluding exclude_idxs,
    and ordered ascending from base index.

    Parameters
    ----------
    exclude_idxs : np.array(int)
        Indices to exclude. First element is the base index from which the remaining indices will be sorted mod ascending.
    n_idxs : int
        Number of indices.

    """
    base_idx = exclude_idxs[0]
    hand_idxs = np.arange(n_idxs)
    remaining_idxs = np.delete(hand_idxs, np.mod(exclude_idxs, n_idxs)) # exclude indices
    # order mod ascending from base
    ordered_idxs = (np.mod(np.sort(np.mod(remaining_idxs - base_idx, n_idxs)) + base_idx, n_idxs)).astype(np.uint)
    return ordered_idxs

def cards_possible(table, discards, hands):
    return util.CARD_NOINFO - table - discards - np.sum(hands, axis=(0, 1))


def norm_hand(hand):
    norm = np.sum(hand, (1, 2))[:, np.newaxis, np.newaxis]
    norm[np.where(norm == 0)[0]] = 1
    hand = hand / norm
    return hand


def norm_card(card):
    norm = np.sum(card)
    norm = 1 if norm==0 else norm
    card = card / norm
    return card


def get_playable_cards(table):
    playable_cards = np.concatenate((np.copy(util.CARD_ZEROS), np.zeros((1, table.shape[1]))), 0)
    playable_cards[np.sum(table, axis=0), np.arange(util.N_COLORS)] = 1
    return playable_cards[:-1, :]


def get_discardable_cards(visible_cards):
    discardable_cards = (np.copy(util.CARD_NOINFO) - visible_cards) != 1
    return discardable_cards


def get_useless_cards(table, discards):
    useless_cards = np.copy(util.CARD_ONES)
    max_color_scores = get_max_color_scores(discards)
    for color_idx in range(util.N_COLORS):
        useless_cards[np.sum(table[:, color_idx]):max_color_scores[color_idx], color_idx] = 0
    useless_cards[0, :] = 0
    return useless_cards


def get_max_color_scores(discards):
    # TODO figure out when not enough turns to play remaining cards
    cards_left = np.copy(util.CARD_NOINFO) - discards
    max_color_scores = util.MAX_NUMBER * np.ones((util.N_COLORS,), np.int8)
    for color_idx in range(util.N_COLORS):
        zero_inds = np.where(cards_left[:, color_idx] == 0)[0]
        if zero_inds.size:
            max_color_scores[color_idx] = np.min(zero_inds)
    return max_color_scores


def get_color_clue_mask(color_idx):
    mask = np.copy(util.CARD_ZEROS)
    mask[:, color_idx] = 1
    return mask


def get_number_clue_mask(number_idx):
    mask = np.copy(util.CARD_ZEROS)
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

    logging.info('Using poss_idx of {}'.format(poss_idx))

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

    logging.info('Received poss_idx of {}'.format(poss_idx))

    action_type = 'play' if not np.mod(poss_idx, 2) else 'discard'
    logging.info(action_type)
    card_idx = np.floor(poss_idx/2).astype(np.int)

    action = (action_type, card_idx)


    return action


def odds_sans_players(hands, clues, table, discards, visible_hands):
    return
