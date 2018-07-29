import numpy as np
import time


def cond_prob(info, poss):
    """
    Return condition probability of a set of cards with partial information.

    Parameters
    ----------
    info : [:, ...]
        Binary array signifying information known about cards. Cards are first dimension, information of each can be
        any dimension.
    poss : [...]
        Integer array of number of available cards of each type.

    Returns
    -------
    probs : [:, ...]
        Float array of same size as 'info' with probibility distribution of each card.

    Notes
    -----
    This is equivalent to enumerating all permutations of available cards, determining which are valid given the known
    information, and calculating the distribution for each card over this set.

    This function is approximately O(k^n) for k valid card types and n cards.

    This implementation is very fast for cards with no information.

    Examples
    --------
    There are four possible card types, two of each of the second and third type. You know some information about four
    of the five cards in your hand.

    probs = cond_prob(np.array([[1, 1, 1, 1], [0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 1], [0, 0, 0, 1]]),
                  np.array([1, 2, 2, 1]))

    """
    n_cards = info.shape[0]
    # any structure on card type is irrelevant here, so flatten higher dimensions
    info_1d = np.reshape(np.copy(info) * np.minimum(poss, 1), (n_cards, np.prod(info.shape[1:])))
    poss_1d = np.reshape(np.copy(poss), poss.size)
    probs = np.zeros(info_1d.shape)

    # sort hand increasing in number of possible card types for faster computation
    n_poss = np.sum(poss_1d)    # total number of cards, including any in a deck
    n_infos = np.sum(info_1d, 1)
    sorted_card_inds = np.argsort(n_infos)
    # distribution of cards with no information can be computed based on distributions of cards with some information
    all_poss_inds = sorted_card_inds[np.where(n_infos[sorted_card_inds] == info_1d[0].size)]
    some_poss_inds = sorted_card_inds[np.where(n_infos[sorted_card_inds] < info_1d[0].size)]
    if some_poss_inds.size:
        combs = comb_count(info_1d[some_poss_inds], poss_1d)
        probs[some_poss_inds] = combs/np.sum(combs[0])
    # this is also the distribution for cards in the deck
    no_info_probs = (poss_1d - np.sum(probs[some_poss_inds], 0))/np.maximum((n_poss - some_poss_inds.size), 1)
    probs[all_poss_inds] = no_info_probs

    # reshape distributions to match input shape
    probs = np.reshape(probs, info.shape)
    return probs


def comb_count(info, poss):
    """
    Return the number of valid permutations of a set of possible cards for a set of cards with some known information.

    Parameters
    ----------
    info : [:, :]
        Binary array signifying information known about cards. Cards are first dimension, card type possibilities are
        the second dimension
    poss : [...]
        Integer array of number of available cards of each type.

    Returns
    -------
    combs : [:, :]
        Integer array with each card position's number of valid permutations containing each card type.

    Notes
    -----
    This is equivalent to enumerating all permutations of available cards, determining which are valid given the known
    information, and counting the frequency for each card over this set.

    This function is approximately O(k^n) for k valid card types and n cards.

    Examples
    --------
    There are four possible card types, two of each of the second and third type. You know some information about four
    of the five cards in your hand.

    probs = comb_count(np.array([[0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 1], [0, 0, 0, 1]]),
                  np.array([1, 2, 2, 1]))

    """
    n_hand = info.shape[0]
    if n_hand == 1:
        # if only one card left, permutations are trivial
        return info[0] * poss[np.newaxis, ...]
    n_poss = info.shape[1]

    combs = np.zeros((n_hand, n_poss))

    # iterate over card type possibilities for first card
    for pp in np.where(info[0])[0]:
        # remove one of card type pp from subsequent card possibilities
        temp_poss = np.copy(poss)
        temp_poss[pp] -= 1
        # recursively count combinations for remaining cards
        sub_combs = comb_count(info[1:] * np.minimum(poss, 1), temp_poss)
        # weight by number of that card type available in possibilities
        combs[1:] += poss[pp] * sub_combs
        combs[0, pp] += poss[pp] * np.sum(sub_combs[0])

    return combs


start_time = time.process_time()

probs = cond_prob(np.array([[1, 1, 1, 1], [0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 1], [0, 0, 0, 1]]),
                  np.array([1, 2, 2, 1]))
print(probs)


info = np.array([[1, 1, 1, 1], [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1]])
possibilities = np.array([1, 1, 1, 1])
probs = cond_prob(info, possibilities)

print(probs)

info = np.array([[0, 1, 1, 1], [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1]])
possibilities = np.array([1, 1, 1, 1])
probs = cond_prob(info, possibilities)

print(probs)

info = np.ones((5, 5, 5))
info[0] = 0
info[0, 4, :] = 1
possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
probs = cond_prob(info, possibilities)

print(probs)

info = np.ones((5, 5, 5))
info[0] = 0
info[0, 0, 0] = 1
info[1] = 0
info[1, 1, :] = 1
info[2] = 0
info[2, 2:3, :] = 1
info[3] = 0
info[3, 1:4, 1:4] = 1
possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
probs = cond_prob(info, possibilities)

print(probs)

info = np.ones((5, 5, 5))
possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
probs = cond_prob(info, possibilities)

print(probs)

info = np.ones((4, 5, 5))
possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
probs = cond_prob(info, possibilities)

print(probs)

info = np.ones((5, 5, 5))
info[:, 0, :] = 0
possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
probs = cond_prob(info, possibilities)

print(probs)
end_time = time.process_time()

print(end_time - start_time)
