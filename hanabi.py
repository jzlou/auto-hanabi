import numpy as np
import sys
import util
import disp
import logging


# class that simulates a hanabi game
class Hanabi:

    def __init__(self, n_players, player_obj):

        self.n_players = n_players
        assert(2 <= self.n_players <= 5)
        self.n_handcards = 4 if self.n_players >= 4 else 5

        # init game state
        self.table = np.copy(util.CARD_ZEROS)
        self.score = 0
        self.n_clues = util.MAX_CLUES
        self.n_fuses = util.MAX_FUSES
        self.curr_player_idx = np.random.randint(0, self.n_players)
        self.discards = np.copy(util.CARD_ZEROS)
        self.n_undealt = util.N_CARDS
        self.eog_turns_left = self.n_players
        self.cheating = False

        self.curr_player_idx = np.random.randint(0, self.n_players)

        # shuffle deck
        self.deck = np.random.permutation(util.N_CARDS)
        # init players
        self.players = [player_obj(self.n_players, self.n_handcards) for player_idx in range(self.n_players)]
        # deal as a human would, one card at a time to each player
        self.hands = np.zeros((self.n_players, self.n_handcards), dtype=np.int8)
        self.n_cards = np.zeros((self.n_players, ), np.int8)
        for card_idx in range(self.n_handcards):
            for player_idx in range(self.n_players):
                self.deal_card(player_idx)

        # print(disp.hands2string(self))
        return

    def play(self):

        logging.debug('Start Game')
        logging.debug(disp.hanabi2str_short(self))

        for player_idx in range(self.n_players):
            self.players[player_idx].start_game(self.curr_player_idx)

        # play game
        while True:
            logging.debug(disp.hanabi2str_short(self))

            self.__next__()

            if self.n_undealt == 0:
                self.eog_turns_left -= 1

            if self.cheating or self.n_fuses == 0 or np.all(self.table == 5) or self.eog_turns_left < 0:
                logging.debug(disp.hanabi2str_short(self))
                self.game_over()
                break

            self.curr_player_idx = util.next_player(self.curr_player_idx, self.n_players)

        return self.score
            
    def __next__(self):
        action_type, action_info = self.players[self.curr_player_idx].play_turn()
        if action_type is 'play':
            self.play_card(action_info)
        elif action_type is 'discard':
            self.discard_card(action_info)
        elif action_type is 'clue':
            self.give_clue(action_info)
        else:
            logging.error('Invalid action: {}'.format(action_type))
            self.cheating = True

        return

    def give_clue(self, clue_info):
        if not self.verify_clue(clue_info):
            self.cheating = True
            return
        self.n_clues -= 1
        rcv_player_idx = util.player_idx_rel2glob(self.curr_player_idx, clue_info[0], self.n_players)
        clue_type = clue_info[1]
        clue_idx = clue_info[2]
        card_idxs = np.sort(clue_info[3])

        logging.debug(disp.clue2str(clue_type, rcv_player_idx, card_idxs, clue_idx) + '\n')

        for player_idx in range(self.n_players):
            rel_player_idx = util.player_idx_glob2rel(self.curr_player_idx, player_idx, self.n_players)
            rel_rcv_player_idx = util.player_idx_glob2rel(rcv_player_idx, player_idx, self.n_players)
            self.players[player_idx].clue_given(rel_player_idx, rel_rcv_player_idx, card_idxs, clue_type, clue_idx)

        return

    def verify_clue(self, clue_info):
        if self.n_clues <= 0:
            logging.error('Clue given when no clues remaining')
            return False
        player_idx = util.player_idx_rel2glob(clue_info[0], self.curr_player_idx, self.n_players)
        clue_type = clue_info[1]
        clue_hint = clue_info[2]
        card_idxs = clue_info[3]
        if clue_type is 'color':
            true_card_idxs = np.where(util.color(self.hands[player_idx, :]) == clue_hint)[0]
        elif clue_type is 'number':
            true_card_idxs = np.where(util.number(self.hands[player_idx, :]) == clue_hint)[0]
        else:
            logging.error('Invalid clue type given ({})'.format(clue_type))
        if not np.array_equal(np.sort(card_idxs), np.sort(true_card_idxs)):
            logging.error('Invalid clue given: Card indices ({}) do not match true card indices ({})'.format(clue_hint, player_idx))
            return False
        return True

    def card_playable(self, card):
        color_idx = util.color_idx(card)
        number_idx = util.number_idx(card)
        card_yet_unplayed = not self.table[number_idx, color_idx]
        previous_card_played = not number_idx or self.table[number_idx - 1, color_idx]
        return card_yet_unplayed and previous_card_played

    def play_card(self, card_idx):
        card = self.hands[self.curr_player_idx][card_idx]
        self.n_cards[self.curr_player_idx] -= 1
        self.hands[self.curr_player_idx] = np.concatenate(
            (np.delete(self.hands[self.curr_player_idx], card_idx), np.array([-1])))

        if self.card_playable(card):
            self.table[util.number_idx(card), util.color_idx(card)] += 1
            self.score += 1
            if util.number(card) == util.MAX_NUMBER:
                self.gain_clue()
            for player_idx in range(self.n_players):
                rel_player_idx = util.player_idx_glob2rel(self.curr_player_idx, player_idx, self.n_players)
                self.players[player_idx].valid_card_played(rel_player_idx, card_idx, card, self.n_clues)
        else:
            self.n_fuses -= 1
            self.discards[util.number_idx(card), util.color_idx(card)] += 1
            for tell_player_idx in range(self.n_players):
                rel_player_idx = util.player_idx_glob2rel(self.curr_player_idx, tell_player_idx, self.n_players)
                self.players[tell_player_idx].invalid_card_played(rel_player_idx, card_idx, card, self.n_fuses)

        logging.debug(disp.play2str(self.curr_player_idx, card_idx, card))
        self.deal_card(self.curr_player_idx)

        return

    def discard_card(self, card_idx):
        card = self.hands[self.curr_player_idx][card_idx]
        self.n_cards[self.curr_player_idx] -= 1
        self.hands[self.curr_player_idx] = np.concatenate(
            (np.delete(self.hands[self.curr_player_idx], card_idx), np.array([-1])))

        self.gain_clue()
        self.discards[util.number_idx(card), util.color_idx(card)] += 1

        # tell players
        for tell_player_idx in range(self.n_players):
            rel_player_idx = util.player_idx_glob2rel(self.curr_player_idx, tell_player_idx, self.n_players)
            self.players[tell_player_idx].card_discarded(rel_player_idx, card_idx, card, self.n_clues)

        logging.debug(disp.discard2str(self.curr_player_idx, card_idx, card))
        self.deal_card(self.curr_player_idx)
        return

    def deal_card(self, player_idx):
        if self.deck.size:
            card = self.deck[0]
            self.deck = self.deck[1:]
            self.n_undealt -= 1
            self.n_cards[player_idx] += 1
            self.hands[player_idx, self.n_cards[player_idx] - 1] = card
            # tell players
            for tell_player_idx in range(self.n_players):
                if tell_player_idx == player_idx:
                    rel_player_idx = -1
                    self.n_cards[player_idx]
                    self.players[tell_player_idx].card_dealt(rel_player_idx, [], self.n_cards[player_idx])
                else:
                    self.n_cards[player_idx]
                    rel_player_idx = util.player_idx_glob2rel(player_idx, tell_player_idx, self.n_players)
                    self.players[tell_player_idx].card_dealt(rel_player_idx, card, self.n_cards[player_idx])
            logging.debug(disp.card_dealt2str(player_idx, card))

        return

    def visible_hands(self, player_idx):
        return np.roll(self.hands[np.arange(self.n_players) != player_idx, ...], -player_idx, 0)
    
    def game_over(self):
        print(disp.table2string(self.table))
        print('GAME OVER! FINAL SCORE: {0}'.format(self.score))
        return

    def gain_clue(self):
        self.n_clues = np.minimum(self.n_clues + 1, util.MAX_CLUES)
        return
