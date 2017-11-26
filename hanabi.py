import numpy as np
import sys
COLORS = np.array(["red", "white", "blue", "green", "yellow"])
NUMBERS = np.array([1,1,1,2,2,3,3,4,4,5])

class PlaysLeftPlayer:
    def __init__(self, id):
        self.id = id;
        return
    
    def play(self):
        Hanabi.play(self.id, 0)

# class that instantiates a hanabi game
class Hanabi:

    def __init__(self, players, N_cards):
        self.table = dict(zip(COLORS, [0] * len(COLORS)))
        self.clues = 8
        self.bombs = 0
        self.next_player = 0
        self.players = players
        self.N_hands = players.len
        self.N_cards = N_cards
        self.deck = np.random.permutation(50)
        self.discards = np.array([])
        
        self.hands = self.deal(self.N_hands*self.N_cards).reshape((self.N_hands, self.N_cards))
        self.print_hands()
    
    def deal(self, N):
        dealt = self.deck[:N]
        self.deck = self.deck[N:]
        return dealt
    
    def print_hand(self, hand_ind):
        cards = self.hands[hand_ind, :]
        numbers = NUMBERS[np.mod(cards,10).astype(int)]
        colors = COLORS[np.floor(cards/10).astype(int)]
        print('{}: '.format(hand_ind), end='')
        for card in range(self.N_cards-1):
            print(' {} {},'.format(colors[card], numbers[card]), end='')
        print(' {} {}'.format(colors[-1], numbers[-1]))
    
    def print_hands(self):
        for hand_ind in range(self.N_hands):
            self.print_hand(hand_ind)
            
    def __next__(self):
        played_card_idx = self.players[self.next_player].play_card_idx
        card = self.hands[hand_idx][played_card_idx]
        number_on_table = self.table[color(card)]
        if number(card) == number_on_table + 1:
            self.table[color(card)] += 1
        else:
            self.bombs += 1
            self.discards.append(card)
            
        # return a new dealt card to the index that the played card was in
        self.hands[hand_idx][card_idx] = self.deal(1)   
        
        if self.bombs >= 3:
            self.game_over()
    
    def color(self, val):
        return COLORS[np.floor(card/10).astype(int)]
    
    def number(self, val):
        return NUMBERS[np.mod(cards,10).astype(int)]
    
    def game_over(self):
        print(np.sum(np.array([table[color] for color in table])))
        sys.exit(0)
    
def print_cards(cards):
    numbers = NUMBERS[np.mod(cards,10).astype(int)]
    colors = COLORS[np.floor(cards/10).astype(int)]
    for card, number in enumerate(numbers):
        print('{}: {} {}'.format(card, colors[card], number))
