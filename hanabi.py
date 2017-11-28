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
        self.next_player = 0
        self.deck = np.random.permutation(50)
        self.discards = np.array([])

        # init players and hands
        self.n_players = len(players)
        assert(2 <= self.n_players <= 5)
        self.players = players
        self.n_heldcards = 4 if self.n_players >= 4 else 5
        self.hands = np.zeros((self.n_players, self.n_heldcards))
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
        played_card_idx = self.players[self.next_player].play_card()
        print(self.next_player)
        print(played_card_idx)
        card = np.array(self.hands[self.next_player][played_card_idx])
        print(card)
        print(type(card))
        print_cards(card)
        number_on_table = self.table[color(card)]
        if number(card) == number_on_table + 1:
            self.table[color(card)] += 1
            self.score = np.sum(self.table)
        else:
            self.bombs += 1
            if self.discards.size:
                self.discards = np.concatenate((self.discards, np.array(card)), 0)
            else:
                self.discards = np.array(card)
            
        # return a new dealt card to the index that the played card was in
        self.hands[self.next_player][played_card_idx] = self.deal(1)

        if self.bombs >= 3:
            self.game_over()
        
        self.next_player = np.mod(self.next_player, self.n_players)
        return
    
    def game_over(self):
        self.score = np.sum(self.table)
        print('GAME OVER! FINAL SCORE: {self.score}')
        sys.exit(0)

    # printing functions
    def print_hands(self):
        for player_idx in range(self.n_players):
            self.print_hand(player_idx)
        return

    def print_hand(self, player_idx):
        cards = self.hands[player_idx, :]
        numbers = np.array(NUMBERS[np.mod(cards, 10).astype(int)])
        colors = np.array(COLORS[np.floor(cards/10).astype(int)])
        print('{}: '.format(player_idx), end='')
        for card in range(self.n_heldcards-1):
            print(' {} {},'.format(colors[card], numbers[card]), end='')
        print(' {} {}'.format(colors[-1], numbers[-1]))
        return


def color(card):
    return COLORS[color_idx(card)]


def color_idx(card):
    return np.floor(card/10).astype(int)


def number(card):
    return NUMBERS[number_idx(card)]


def number_idx(card):
    return np.mod(card, 10).astype(int)


def print_cards(cards):
    if cards.size > 1:
        card = cards
        print('{}: {} {}'.format(card, color(card), number(card)))
    else:
        for card in cards:
            print('{}: {} {}'.format(card, color(card), number(card)))
    return


h = Hanabi([PlaysLeftPlayer(player_idx) for player_idx in range(4)])
