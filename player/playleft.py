import util
import numpy as np


class PlayLeft:
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
        self.hands = np.repeat(util.CARD_ZEROS[np.newaxis, np.newaxis, ...], self.n_players, self.n_handcards, 1)
        self.clued_hands = np.repeat(util.CARD_ZEROS[np.newaxis, np.newaxis, ...], self.n_players, self.n_handcards, 1)
        self.info_hands = np.repeat(util.CARD_ZEROS[np.newaxis, np.newaxis, ...], self.n_players, self.n_handcards, 1)
        self.odds_hands = np.repeat(util.CARD_ZEROS[np.newaxis, np.newaxis, ...], self.n_players, self.n_handcards, 1)
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
        action = ('play', 0)
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
        keep_inds = np.where(np.arange(self.n_cards[player_idx]) != card_idx)[0]
        self.n_cards[player_idx] -= 1
        self.hands[player_idx][:self.n_cards[player_idx], ...] = self.hands[player_idx][keep_inds, ...]
        self.hands[player_idx][self.n_cards[player_idx], ...] = util.CARD_ZEROS
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
        keep_inds = np.where(np.arange(self.n_cards[player_idx]) != card_idx)[0]
        self.n_cards[player_idx] -= 1
        self.hands[player_idx][:self.n_cards[player_idx], ...] = self.hands[player_idx][keep_inds, ...]
        self.hands[player_idx][self.n_cards[player_idx], ...] = util.CARD_ZEROS
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
        keep_inds = np.where(np.arange(self.n_cards[player_idx]) != card_idx)[0]
        self.n_cards[player_idx] -= 1
        self.hands[player_idx][:self.n_cards[player_idx], ...] = self.hands[player_idx][keep_inds, ...]
        self.hands[player_idx][self.n_cards[player_idx], ...] = util.CARD_ZEROS
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
        assert(self.n_cards[player_idx] == n_cards)
        if player_idx == -1 or player_idx == self.n_players:
            self.hands[player_idx][self.n_cards[player_idx] - 1, ...] = util.CARD_NOINFO - self.table - self.discards - np.sum(self.hands[:self.n_players - 1][self.n_cards[player_idx] - 1, ...])
        else:
            self.hands[player_idx][self.n_cards[player_idx] - 1, ...] = util.card2info(card)
        return

    def cards_possible(self):
        util.CARD_NOINFO - self.table - self.discards - np.sum(self.hands[:self.n_players - 1, :, ...])