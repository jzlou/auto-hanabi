import numpy as np
import sys
import util
import disp
import logging


# class that stores public information about hanabi game
class HanabiPublicInfo:
    # TODO figure out how to make these only editable in this script
    def __init__(self, n_players):
        self.n_players = n_players
        assert(2 <= self.n_players <= 5)
        self.n_heldcards = 4 if self.n_players >= 4 else 5

        # init game state
        self.table = np.zeros((util.N_UNIQUE_NUMBERS, ), dtype=int)
        self.score = 0
        self.clues = util.MAX_CLUES
        self.fuse = 3
        self.curr_player_idx = 0
        self.discards = np.copy(util.CARD_ZEROS)
        self.deck_size = util.N_CARDS
        self.eog_turns_left = self.n_players

        self.curr_player_idx = np.random.randint(0, self.n_players)
        return


# class that simulates a hanabi game
class Hanabi:

    def __init__(self, n_players, player_obj):
        self.info = HanabiPublicInfo(n_players)

        # shuffle deck
        self.deck = np.random.permutation(util.N_CARDS)
        # init players
        self.players = [player_obj(player_idx, self.info) for player_idx in range(self.info.n_players)]
        # deal as a human would, one card at a time to each player
        self.hands = np.zeros((self.info.n_players, self.info.n_heldcards), dtype=np.int)
        for card_idx in range(self.info.n_heldcards):
            for hand_idx in range(self.info.n_players):
                self.hands[hand_idx, card_idx] = self.deal_card()

        # print(disp.hands2string(self))
        return

    def play(self):

        logging.debug('Start Game')
        logging.debug(disp.hanabi2str_short(self))

        for player_idx in range(self.info.n_players):
            self.players[player_idx].init_game(self.visible_hands(player_idx))

        # play game
        while True:
            logging.debug(disp.hanabi2str_short(self))

            self.__next__()

            if self.info.deck_size == 0:
                self.info.eog_turns_left -= 1

            if self.info.fuse == 0 or np.all(self.info.table == 5) or self.info.eog_turns_left < 0:
                logging.debug(disp.hanabi2str_short(self))
                self.game_over()
                break

            self.info.curr_player_idx = util.next_player(self.info.curr_player_idx, self.info.n_players)

        return self.info.score
            
    def __next__(self):
        action = self.players[self.info.curr_player_idx].play_turn(self.info, self.visible_hands(self.info.curr_player_idx))
        if action[0] is 'play' or action[0] is 'discard':
            card_idx = action[1][0]
            card = self.hands[self.info.curr_player_idx][card_idx]
            self.hands[self.info.curr_player_idx] = np.concatenate((np.delete(self.hands[self.info.curr_player_idx], card_idx), np.array([-1])))
            if action[0] is 'play':
                logging.debug(disp.play2str(self.info.curr_player_idx, card_idx, card))
                self.play_card(card)
            elif action[0] is 'discard':
                logging.debug(disp.discard2str(self.info.curr_player_idx, card_idx, card))
                self.info.clues = np.minimum(self.info.clues + 1, util.MAX_CLUES)
                self.discard_card(card)
            # pick up new card
            dealt_card = self.deal_card()
            self.hands[self.info.curr_player_idx][-1] = dealt_card

            for player_idx in np.arange(self.info.n_players)[np.where(np.arange(self.info.n_players) != self.info.curr_player_idx)[0]]:
                self.players[player_idx].get_action(action, self.info)
                self.players[self.info.curr_player_idx].get_card(self.info.curr_player_idx, dealt_card)

        elif action[0] is 'clue':
            if self.info.clues <= 0:
                logging.error('Clue given when no clues remaining')
                return
            self.info.clues -= 1
            clue = action[1]
            player_idx = util.player_idx_rel2glob(self.info.curr_player_idx, clue[0], self.info.n_players)
            self.verify_clue(clue)
            clue_type = clue[1]
            clue_hint = clue[2]
            card_idxs = clue[3]

            logging.debug(disp.clue2str(clue_type, player_idx, card_idxs, clue_hint) + '\n')
        else:
            logging.error('Invalid action: {}'.format(action[0]))

        for player_idx in range(self.info.n_players):
            self.players[player_idx].get_action(action, self.info)

        return

    def verify_clue(self, clue):
        player_idx = util.player_idx_rel2glob(clue[0], self.info.curr_player_idx, self.info.n_players)
        clue_type = clue[1]
        clue_hint = clue[2]
        card_idxs = clue[3]
        if clue_type is 'color':
            true_card_idxs = np.where(util.color(self.hands[player_idx, :]) is clue_hint)[0]
        elif clue_type is 'number':
            true_card_idxs = np.where(util.number(self.hands[player_idx, :]) == clue_hint)[0]
        else:
            logging.error('Invalid clue type given ({})'.format(clue_type))
            sys.exit()
        if not np.array_equal(np.sort(card_idxs), np.sort(true_card_idxs)):
            logging.error('Invalid clue given: Card indices ({}) do not match true card indices ({})'.format(clue_hint, player_idx))
            sys.exit()
        return

    def play_card(self, card):
        if util.number(card) == self.info.table[util.color_idx(card)] + 1:
            self.info.table[util.color_idx(card)] += 1
            self.info.score = np.sum(self.info.table)
            if util.number(card) == 5:
                self.info.clues = np.minimum(self.info.clues + 1, util.MAX_CLUES)
        else:
            logging.debug(disp.invalid_play2str(card))
            self.info.fuse -= 1
            self.discard_card(card)
        return

    def discard_card(self, card):
        self.info.discards[util.number_idx(card), util.color_idx(card)] += 1
        return

    def deal_card(self):
        if self.deck.size:
            card = self.deck[0]
            self.deck = self.deck[1:]
            self.info.deck_size -= 1
        else:
            card = -1
        return card

    def visible_hands(self, player_idx):
        return np.roll(self.hands[np.arange(self.info.n_players) != player_idx, ...], -player_idx, 0)
    
    def game_over(self):
        self.info.score = np.sum(self.info.table)
        # print(disp.table2string(self.table))
        # print('GAME OVER! FINAL SCORE: {0}'.format(self.score))
        return
