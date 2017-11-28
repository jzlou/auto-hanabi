import numpy as np
import sys
import util
import disp


# class that instantiates a hanabi game
class Hanabi:

    def __init__(self, players):
        # init game state
        self.table = np.zeros((5, ), dtype=int)
        self.score = 0
        self.clues = 8
        self.bombs = 0
        self.curr_player = 0
        self.deck = np.random.permutation(50)
        self.discards = np.array([])

        # init players and hands
        self.n_players = len(players)
        assert(2 <= self.n_players <= 5)
        self.players = players
        self.n_heldcards = 4 if self.n_players >= 4 else 5
        self.hands = np.zeros((self.n_players, self.n_heldcards), dtype=np.int)
        # deal as a human would, one card at a time to each player
        for card_idx in range(self.n_heldcards):
            for hand_idx in range(self.n_players):
                self.hands[hand_idx, card_idx] = self.deal_card()

        disp.print_hands(self)

        # play game
        while True:
            self.__next__()

    def deal_card(self):
        if self.deck.size:
            card = self.deck[1]
            self.deck = self.deck[1:]
        else:
            # deck is empty, only happens when player has no turns left anyways
            card = -1
        return card
            
    def __next__(self):
        # TODO add clue giving and discarding
        play_card_idx = self.players[self.curr_player].play_card()
        played_card = self.hands[self.curr_player][play_card_idx]
        print(self.curr_player)
        print(played_card)
        if util.number(played_card) == self.table[util.color_idx(played_card)] + 1:
            self.table[util.color_idx(played_card)] += 1
            self.score = np.sum(self.table)
        else:
            self.bombs += 1
            if self.discards.size:
                self.discards = np.concatenate((self.discards, np.array([played_card])))
            else:
                self.discards = np.array([played_card])
            
        # return a new dealt card to the index that the played card was in
        self.hands[self.curr_player][play_card_idx] = self.deal_card()

        if self.bombs >= 3:
            self.game_over()
        
        self.curr_player = np.mod(self.curr_player, self.n_players)
        return
    
    def game_over(self):
        self.score = np.sum(self.table)
        print(disp.table2string(self.table))
        print('GAME OVER! FINAL SCORE: {0}'.format(self.score))
        sys.exit(0)
