import numpy as np
import sys
import util
import disp


# class that stores public information about hanabi game
class HanabiPublicInfo:
    def __init__(self, n_players):
        self.n_players = n_players
        assert(2 <= self.n_players <= 5)
        self.n_heldcards = 4 if self.n_players >= 4 else 5

        # init game state
        self.table = np.zeros((5, ), dtype=int)
        self.score = 0
        self.clues = 8
        self.bombs = 0
        self.curr_player_idx = 0
        self.discards = np.array([])

        self.curr_player_idx = np.random.randint(0, self.n_players)
        return


# class that simulates a hanabi game
class Hanabi:

    def __init__(self, n_players, player_obj):
        self.info = HanabiPublicInfo(n_players)

        # shuffle deck
        self.deck = np.random.permutation(50)
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

        # play game
        while True:
            self.__next__()

            if self.info.bombs >= 3 or np.all(self.info.table == 5):
                self.game_over()
                break

            self.info.curr_player_idx = np.mod(self.info.curr_player_idx + 1, self.info.n_players)

        return self.score

    def deal_card(self):
        card = self.deck[1]
        self.deck = self.deck[1:]
        return card
            
    def __next__(self):
        # TODO add clue giving and discarding
        play_card_idx = self.players[self.info.curr_player_idx].play_turn(self.info)
        played_card = self.hands[self.info.curr_player_idx][play_card_idx]
        self.hands[self.info.curr_player_idx] = np.concatenate((np.delete(self.hands[self.info.curr_player_idx], play_card_idx), np.array([-1])))
        if util.number(played_card) == self.info.table[util.color_idx(played_card)] + 1:
            self.info.table[util.color_idx(played_card)] += 1
            self.score = np.sum(self.info.table)
            if util.number(played_card) == 5:
                self.info.clues += 1
        else:
            self.info.bombs += 1
            if self.discards.size:
                self.discards = np.concatenate((self.discards, np.array([played_card])))
            else:
                self.discards = np.array([played_card])

        if self.deck.size:
            self.hands[self.info.curr_player_idx][-1] = self.deal_card()
            self.players[self.info.curr_player_idx].get_card()

        return
    
    def game_over(self):
        self.info.score = np.sum(self.info.table)
        # print(disp.table2string(self.table))
        # print('GAME OVER! FINAL SCORE: {0}'.format(self.score))
        return
