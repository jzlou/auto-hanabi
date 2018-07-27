import numpy as np
import time


def cond_prob(info, possibilities):
    temp_info = np.reshape(np.copy(info)*np.minimum(possibilities, 1), (info.shape[0], np.int(np.round(info.size/info.shape[0]))))
    temp_poss = np.reshape(np.copy(possibilities), possibilities.size)
    n_poss_per_card = np.sum(temp_info, 1)
    sorted_card_inds = np.argsort(-n_poss_per_card)
    all_poss_inds = sorted_card_inds[np.where(n_poss_per_card[sorted_card_inds] == temp_info[0].size)]
    some_poss_inds = sorted_card_inds[np.where(n_poss_per_card[sorted_card_inds] < temp_info[0].size)]
    probs = np.zeros(temp_info.shape)
    if some_poss_inds.size:
        combs = comb_count(temp_info[some_poss_inds], temp_poss)
        probs[some_poss_inds] = combs/np.sum(combs[-1])
    # this is also the distribution for cards in the deck
    no_info_probs = (temp_poss - np.sum(probs[some_poss_inds], 0))/np.maximum((np.sum(temp_poss) - some_poss_inds.size), 1)
    probs[all_poss_inds] = no_info_probs

    probs = np.reshape(probs, info.shape)
    return probs


def comb_count(info, possibilities):
    n_hand = info.shape[0]
    if n_hand == 1:
        return info[-1]*possibilities[np.newaxis, ...]
    n_poss = info.shape[1]

    combs = np.zeros((n_hand, n_poss) )

    this_card_poss = info[-1]*possibilities

    for pp in np.where(this_card_poss)[0]:
        temp_poss = np.copy(possibilities)
        temp_poss[pp] -= 1
        sub_combs = comb_count(info[:-1], temp_poss)
        combs[:-1] += possibilities[pp]*sub_combs
        combs[-1, pp] += possibilities[pp]*np.sum(sub_combs[-1])

    return combs

start_time = time.process_time()

# info = np.array([[1, 1, 1, 1], [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1]])
# possibilities = np.array([1, 1, 1, 1])
# probs = cond_prob(info, possibilities)
#
# print(probs)
#
# info = np.array([[0, 1, 1, 1], [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1]])
# possibilities = np.array([1, 1, 1, 1])
# probs = cond_prob(info, possibilities)
#
# print(probs)
#
# info = np.ones((5, 5, 5))
# info[0] = 0
# info[0, 4, :] = 1
# possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
# probs = cond_prob(info, possibilities)
#
# print(probs)
#
# info = np.ones((5, 5, 5))
# info[0] = 0
# info[0, 0, 0] = 1
# info[1] = 0
# info[1, 1, :] = 1
# info[2] = 0
# info[2, 2:3, :] = 1
# info[3] = 0
# info[3, 2:, :] = 1
# possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
# probs = cond_prob(info, possibilities)
#
# print(probs)
#
# info = np.ones((5, 5, 5))
# possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
# probs = cond_prob(info, possibilities)
#
# print(probs)
#
# info = np.ones((4, 5, 5))
# possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
# probs = cond_prob(info, possibilities)
#
# print(probs)

info = np.ones((5, 5, 5))
# info[:, 0, :] = 0
possibilities = np.tile(np.array([3, 2, 2, 2, 1])[:, np.newaxis], (1, 5))
probs = cond_prob(info, possibilities)

print(probs)
end_time = time.process_time()

print(end_time - start_time)
