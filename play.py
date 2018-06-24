from hanabi import Hanabi
import numpy as np
from player.playsleft import PlaysLeftPlayer
from player.playleft import PlayLeft
import util
from player.playleft_basic import PlayLeftBasic
from player.clueones import ClueOnes
from player.clue12 import Clue12
from player.clueplayableleft import CluePlayableLeft
from player.cluelowest import ClueLowest
import logging
import sys
import matplotlib.pyplot as plt
import os

N_PLAYERS = 4

results_dir = 'results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# logging.basicConfig(filename='hanabi.log', filemode='w', level=logging.DEBUG, format='%(message)s')
logging.basicConfig(filename='hanabi.log', filemode='w', level=logging.DEBUG, format='%(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
# ch.setLevel(logging.DEBUG)
ch.setLevel(logging.WARNING)
log.addHandler(ch)

# still print to stdout
# but also save output to log

PlayerTypes = (PlayLeftBasic, ClueOnes, Clue12, ClueLowest)
redo = np.array([False, True, True, False])
N_types = len(PlayerTypes)
N_trials = 2**8
scores = np.zeros((N_types, N_trials), dtype=int)
hists = np.zeros((N_types, util.N_PLAYABLE+1))
bins = np.arange(util.N_PLAYABLE+2) - .5

for tt, PlayerType in enumerate(PlayerTypes):
    results_fn = os.path.join(results_dir, PlayerType.__name__ + '.npy')
    if redo[tt] or not os.path.isfile(results_fn):
        np.random.seed(0)
        for nn in range(N_trials):
            h = Hanabi(N_PLAYERS, PlayerType)
            scores[tt, nn] = h.play()
        np.save(results_fn, scores[tt])
    else:
        scores[tt] = np.load(results_fn)
    hists[tt, :] = np.flip(np.cumsum(np.flip(np.histogram(scores[tt], bins)[0], 0)), 0).astype(np.double)/N_trials

plt.plot(hists.T)
plt.xlabel('Score of At Least')
plt.ylabel('Probability')
plt.legend([PlayerType.__name__ for PlayerType in PlayerTypes])
plt.xlim([0, util.N_PLAYABLE])
plt.ylim([0, 1])
plt.grid()
plt.savefig('results.png', bbox_inches='tight')

print(np.mean(scores, axis=1))
print(np.max(scores, axis=1))

np.savetxt(os.path.join(results_dir, 'scores.txt'), scores, fmt='%i')
