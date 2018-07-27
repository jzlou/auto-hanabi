import numpy as np
import time

def cond_prob(info, possibilities):
    # TODO sort info by number of possibilities, so cards that can be many things are evaluated last
    # TODO once sorted, can drop last N cards that can be anything. This prob can be found from other probs, since all
    # cards with no info (like cards from the deck) have same distribution among themselves, and must make total sum
    # probability for each specific card type sum to 1
    # prob for card with no info = (1 - np.sum(probs, 0))/(n cards left including deck cards and cards with no info)
    temp_info = np.reshape(np.copy(info)*np.minimum(possibilities, 1), (info.shape[0], np.int(np.round(info.size/info.shape[0]))))
    temp_poss = np.reshape(np.copy(possibilities), possibilities.size)
    combs = comb_count(temp_info, temp_poss)
    probs = np.reshape(combs/np.sum(combs[-1]), info.shape)
    return probs


def comb_count(info, possibilities):
    n_hand = info.shape[0]
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

start_time = time.process_time()
info = np.array([[1, 1, 1, 1], [1, 1, 0, 0], [0, 1, 1, 1], [0, 0, 0, 1]])
possibilities = np.array([1, 1, 1, 1])
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
