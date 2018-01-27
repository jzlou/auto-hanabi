import player.clues
import util
import numpy as np


class ClueLowest:
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
        self.curr_player_idx = None
        self.n_fuses = util.MAX_FUSES
        self.n_clues = util.MAX_CLUES
        self.n_undealts = util.N_CARDS
        self.hands = np.tile(util.CARD_ZEROS[np.newaxis, np.newaxis, ...], (self.n_players, self.n_handcards, 1, 1))
        self.clues_hands = np.tile(util.CARD_ONES[np.newaxis, np.newaxis, ...],
                                   (self.n_players, self.n_handcards, 1, 1))
        self.info_hands = np.tile(util.CARD_ZEROS[np.newaxis, np.newaxis, ...],
                                  (self.n_players, self.n_handcards, 1, 1))
        self.odds_hands = np.tile(util.CARD_ZEROS[np.newaxis, np.newaxis, ...],
                                  (self.n_players, self.n_handcards, 1, 1))
        self.n_cards = np.zeros((self.n_players,), np.int)
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
        # determine card index to play
        playable_cards = get_playable_cards(self.table)
        discardable_cards = get_discardable_cards(self.table, self.discards)
        useless_cards = get_useless_cards(self.table, self.discards)
        hand_odds = norm_hand(self.hands[-1, ...]*self.clues_hands[-1, ...])
        odds_playable = np.sum(playable_cards[np.newaxis, ...] * hand_odds, (2, 1))
        odds_discardable = np.sum(discardable_cards[np.newaxis, ...] * hand_odds, (2, 1))
        odds_useless = np.sum(useless_cards[np.newaxis, ...] * hand_odds, (2, 1))
        if np.max(odds_playable) >= np.max(odds_useless):
            card_idx = np.argmax(odds_playable)
            action = ('play', card_idx)
            action_odds = odds_playable[card_idx]
        else:
            card_idx = np.argmax(odds_useless)
            action = ('discard', card_idx)
            action_odds = odds_useless[card_idx]
        if self.n_clues > 0 and action_odds < .5:
            # clue next player where lowest value cards are
            next_player_rel_idx = 0
            clue_hint = np.where(np.sum(self.hands[next_player_rel_idx, ...], axis=(0, 2)))[0][0]
            clue_type = 'number'
            clue_idxs = np.where(np.sum(self.hands[next_player_rel_idx, :, clue_hint, :], axis=1))[0]
            clue = (next_player_rel_idx, clue_type, clue_hint, clue_idxs)
            action = ('clue', clue)

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
            self.hands[player_idx][self.n_cards[player_idx] - 1, ...] = cards_possible(self.table, self.discards,
                                                                                       self.hands[:-1, ...])
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


def cards_possible(table, discards, hands):
    return util.CARD_NOINFO - table - discards - np.sum(hands, axis=(0, 1))


def norm_hand(hand):
    norm = np.sum(hand, (1, 2))[:, np.newaxis, np.newaxis]
    norm[np.where(norm == 0)[0]] = 1
    hand = hand / norm
    return hand


def get_playable_cards(table):
    playable_cards = np.concatenate((np.copy(util.CARD_ZEROS), np.zeros((1, table.shape[1]))), 0)
    playable_cards[np.sum(table, axis=0), np.arange(util.N_COLORS)] = 1
    return playable_cards[:-1, :]


def get_discardable_cards(table, discards):
    discardable_cards = (np.copy(util.CARD_NOINFO) - table - discards) != 1
    return discardable_cards


def get_useless_cards(table, discards):
    useless_cards = np.copy(util.CARD_ONES)
    max_color_scores = get_max_color_scores(discards)
    for color_idx in range(util.N_COLORS):
        useless_cards[np.sum(table[:, color_idx]):max_color_scores[color_idx], color_idx] = 0
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
