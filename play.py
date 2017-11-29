from hanabi import Hanabi
import numpy as np
from player.playsleft import PlaysLeftPlayer

n_trials = 10000
scores = np.zeros((n_trials, ), dtype=int)
for nn in range(n_trials):
    h = Hanabi([PlaysLeftPlayer(player_idx) for player_idx in range(4)])
    scores[nn] = h.play()

print(np.mean(scores))
print(np.max(scores))
