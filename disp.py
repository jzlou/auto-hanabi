import util


def cards2string(cards):
    if cards.size < 2:
        card = cards
        string = card2string(card)
    else:
        string = ''
        for card in cards:
            string += card2string(card) + ', '
        string = string[:-2]
    return string


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
def hands2string(hanabi):
    string = ''
    for player_idx in range(hanabi.n_players):
        string += hand2string(hanabi, player_idx) + '\n'
    return string[:-1]


def hand2string(hanabi, player_idx):
    return '{0}: {1}'.format(player_idx, cards2string(hanabi.hands[player_idx, :]))
