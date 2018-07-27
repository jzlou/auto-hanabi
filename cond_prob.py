import numpy as np


def cond_prob(info, possibilities):
    temp_info = np.reshape(np.copy(info)*np.minimum(possibilities, 1), (info.shape[0], np.int(np.round(info.size/info.shape[0]))))
    temp_poss = np.reshape(np.copy(possibilities), possibilities.size)
    combs = comb_count(temp_info, temp_poss)
    return np.reshape(combs/np.sum(combs[-1]), info.shape)


def comb_count(info, possibilities):
    n_hand = info.shape[0]
    if not n_hand:
        return (0, [])
    if n_hand == 1:
        return info[-1]*possibilities[np.newaxis, ...]
    n_poss = info.shape[1]

    combs = np.zeros((n_hand, n_poss) )

    this_card_poss = info[-1]*possibilities
    # this_card_neg_poss = (1 - info[-1])*possibilities

    # if np.sum(this_card_neg_poss) < np.sum(this_card_poss):
    #     negate = True
    #     this_card_poss = this_card_neg_poss

    for pp in np.where(this_card_poss)[0]:
        temp_poss = np.copy(possibilities)
        temp_poss[pp] -= 1
        sub_combs = comb_count(info[:-1], temp_poss)
        combs[:-1] += possibilities[pp]*sub_combs
        combs[-1, pp] += possibilities[pp]*np.sum(sub_combs[-1])


    return combs


# info = np.array([[1, 1, 1, 1], [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1]])
# possibilities = np.array([1, 1, 1, 1])

# info = np.ones((5, 5, 5))
# possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))

info = np.ones((4, 5, 5))
possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))

# info = np.ones((5, 5, 5))
# info[:, 0, :] = 0
# possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))

probs = cond_prob(info, possibilities)

print(probs)
