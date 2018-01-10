from hanabi import Hanabi
import numpy as np
from player.playsleft import PlaysLeftPlayer
from player.playleft import PlayLeft
from player.playleft_basic import PlayLeftBasic
from player.clueonesifclue import ClueOnesIfClue
from player.clueplayableleft import CluePlayableLeft
import logging
import sys

N_PLAYERS = 4

# logging.basicConfig(filename='hanabi.log', filemode='w', level=logging.DEBUG, format='%(message)s')
logging.basicConfig(filename='hanabi.log', filemode='w', level=logging.DEBUG, format='%(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# ch.setLevel(logging.WARNING)
log.addHandler(ch)

# still print to stdout
# but also save output to log

n_trials = 1
np.random.seed(0)
scores = np.zeros((n_trials, ), dtype=int)
for nn in range(n_trials):
    h = Hanabi(N_PLAYERS, CluePlayableLeft)
    scores[nn] = h.play()

print(np.mean(scores))
print(np.max(scores))
