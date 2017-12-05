from hanabi import Hanabi
import numpy as np
from player.playsleft import PlaysLeftPlayer
from player.clueonesifclue import ClueOnesIfClue
import logging
import sys

logging.basicConfig(filename='hanabi.log', filemode='w', level=logging.DEBUG, format='%(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
log.addHandler(ch)

# still print to stdout
# but also save output to log

n_trials = 1
scores = np.zeros((n_trials, ), dtype=int)
for nn in range(n_trials):
    h = Hanabi(4, ClueOnesIfClue)
    scores[nn] = h.play()

print(np.mean(scores))
print(np.max(scores))
