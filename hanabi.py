import numpy as np
import sys

COLORS = np.array(["red", "white", "blue", "green", "yellow"])
NUMBERS = np.array([1, 1, 1, 2, 2, 3, 3, 4, 4, 5])


class PlaysLeftPlayer:
    def __init__(self, player_idx):
        self.player_idx = player_idx
        return

    def play_card(self):
        return 0


# class that instantiates a hanabi game
class Hanabi:

    def __init__(self, players):
        # init game state
        self.table = np.zeros((5, ))
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
            self.hands[:, card_idx] = self.deal(self.n_players)

        self.print_hands()

        # play game
        while True:
            self.__next__()

    def deal(self, n_cards):
        dealt_cards = self.deck[:n_cards]
        self.deck = self.deck[n_cards:]
        return dealt_cards
            
    def __next__(self):
        # TODO add clue giving and discarding
        play_card_idx = self.players[self.curr_player].play_card()
        played_card = self.hands[self.curr_player][play_card_idx]
        print(self.curr_player)
        print(played_card)
        if number(played_card) == self.table[color_idx(played_card)] + 1:
            self.table[color_idx(played_card)] += 1
            self.score = np.sum(self.table)
        else:
            self.bombs += 1
            if self.discards.size:
                self.discards = np.concatenate((self.discards, np.array([played_card])))
            else:
                self.discards = np.array([played_card])
            
        # return a new dealt card to the index that the played card was in
        # TODO handle end of game when no new cards? - only happens when player has no turns left anyways
        self.hands[self.curr_player][play_card_idx] = self.deal(1)

        if self.bombs >= 3:
            self.game_over()
        
        self.curr_player = np.mod(self.curr_player, self.n_players)
        return
    
    def game_over(self):
        self.score = np.sum(self.table)
        print('GAME OVER! FINAL SCORE: {0}'.format(self.score))
        sys.exit(0)

    # printing functions
    def print_hands(self):
        for player_idx in range(self.n_players):
            self.print_hand(player_idx)
        return

    def print_hand(self, player_idx):
        cards = self.hands[player_idx, :]
        print('{0}: {1}'.format(player_idx, cards2string(cards)))
        return


def color(card):
    return COLORS[color_idx(card)]


def color_idx(card):
    return np.floor(card/10).astype(int)


def number(card):
    return NUMBERS[number_idx(card)]


def number_idx(card):
    return np.mod(card, 10).astype(int)


def cards2string(cards):
    if cards.size < 2:
        card = cards
        cards2string = card2string(card)
    else:
        cards2string = ''
        for card in cards:
            cards2string += card2string(card) + ', '
    return cards2string


def card2string(card):
    return '{0: <6} {1}'.format(color(card), number(card))


h = Hanabi([PlaysLeftPlayer(player_idx) for player_idx in range(4)])
