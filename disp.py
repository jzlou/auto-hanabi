import util


def cards2string(cards):
    if cards.size < 2:
        card = cards
        cards2string = card2string(card)
    else:
        cards2string = ''
        for card in cards:
            cards2string += card2string(card) + ', '
        cards2string = cards2string[:-2]
    return cards2string


def card2string(card):
    return '{0: >6} {1}'.format(util.color(card), util.number(card))


def table2string(table):
    string = ''
    for number in range(1, 6):
        for color_idx in range(5):
            if table[color_idx] >= number:
                string += '{0: >6} {1}, '.format(util.COLORS[color_idx], number)
            else:
                string += '        , '
        string = string[:-2] + '\n'
    return string


# printing functions
def print_hands(hanabi):
    for player_idx in range(hanabi.n_players):
        print_hand(hanabi, player_idx)
    return


def print_hand(hanabi, player_idx):
    cards = hanabi.hands[player_idx, :]
    print('{0}: {1}'.format(player_idx, cards2string(cards)))
    return