import util
import numpy as np


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


def card2string_short(card):
    return '{0}{1}'.format(util.color_short(card), util.number(card))


def table2string(table):
    string = ''
    for number in range(1, util.MAX_NUMBER+1):
        for color_idx in range(util.N_COLORS):
            if table[color_idx] >= number:
                string += '{0: >6} {1}, '.format(util.COLORS[color_idx], number)
            else:
                string += '        , '
        string = string[:-2] + '\n'
    return string


def table2string_short(table):
    string = ' ' + np.array2string(util.COLORS_SHORT, formatter={'all': lambda x: "%3s" % x})[1:-1] + ' \n'
    string += np.array2string(table, formatter={'all': lambda x: "%3i" % x})
    return string


# printing functions
def hands2string(hanabi):
    string = ''
    for player_idx in range(hanabi.n_players):
        string += hand2string(hanabi, player_idx) + '\n'
    return string[:-1]


def hands2string_short(hanabi):
    string = ''
    for player_idx in range(hanabi.info.n_players):
        hand_str = hand2string_short(hanabi, player_idx)
        if player_idx==hanabi.info.curr_player_idx:
            string += '>' + hand_str + '<'
        else:
            string += ' ' + hand_str + ' '
        if player_idx!=hanabi.info.n_players:
            string += '\n'
    return string


def hand2string(hanabi, player_idx):
    return '{0}: {1}'.format(player_idx, cards2string(np.flipud(hanabi.hands[player_idx, :])))


def hand2string_short(hanabi, player_idx):
    hand = np.flipud(hanabi.hands[player_idx, ...])
    return '{0}: {1}'.format(player_idx, '[%s]' % ', '.join(map(str, [card2string_short(card) for card in hand])))


def counters2string(info):
    return '{0} Now Playing  {1} Clues  {2} Bombs  {3} Deck'.format(info.curr_player_idx, info.clues, info.bombs, info.deck_size)


def counters2string_short(info):
    return '{0} Clues  {1} Fuse  {2} Deck Size'.format(info.clues, info.fuse, info.deck_size)


def hanabi2str_short(hanabi):
    string = '\n{0}\n{1}\n\n{2}\n'.format(hands2string_short(hanabi), counters2string_short(hanabi.info), table2string_short(hanabi.info.table))
    return string


def color_clue2str(player_idx, card_idxs, clue_hint):
    if card_idxs.size > 1:
        string = 'Player {}, cards {} are {}'.format(player_idx, card_idxs, clue_hint)
    else:
        string = 'Player {}, card {} is {}'.format(player_idx, card_idxs, clue_hint)
    return string


def number_clue2str(player_idx, card_idxs, clue_hint):
    if card_idxs.size > 1:
        string = 'Player {}, cards {} are {}s'.format(player_idx, card_idxs, clue_hint)
    else:
        string = 'Player {}, card {} is a {}'.format(player_idx, card_idxs, clue_hint)
    return string


def clue2str(clue_type, player_idx, card_idxs, clue_hint):
    if clue_type is 'color':
        string = color_clue2str(player_idx, card_idxs, clue_hint)
    else:
        string = number_clue2str(player_idx, card_idxs, clue_hint)
    return string


def play2str(player_idx, card_idx, card):
    string = 'Player {} plays card [{}], a {} {}'.format(player_idx, card_idx, util.color(card), util.number(card))
    return string


def discard2str(player_idx, card_idx, card):
    string = 'Player {} discards card [{}], a {} {}'.format(player_idx, card_idx, util.color(card), util.number(card))
    return string


def invalid_play2str(card):
    string = 'A {} {} is not playable, fuse reduced'.format(util.color(card), util.number(card))
    return string
