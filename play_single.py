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
from player.cluekeying import ClueKeying
import logging
import sys
import matplotlib.pyplot as plt
import os

N_PLAYERS = 4

results_dir = 'results'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# logging.basicConfig(filename='hanabi.log', filemode='w', level=logging.DEBUG, format='%(message)s')
logging.basicConfig(filename='hanabi_single.log', filemode='w', level=logging.DEBUG, format='%(message)s')
log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
# ch.setLevel(logging.WARNING)
log.addHandler(ch)

# still print to stdout
# but also save output to log

PlayerTypes = (ClueKeying, )
N_types = len(PlayerTypes)
N_trials = 1
scores = np.zeros((N_types, N_trials), dtype=int)

for tt, PlayerType in enumerate(PlayerTypes):
    np.random.seed(0)
    for nn in range(N_trials):
        h = Hanabi(N_PLAYERS, PlayerType)
        scores[tt, nn] = h.play()

print(np.mean(scores, axis=1))
print(np.max(scores, axis=1))
