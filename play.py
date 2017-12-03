from hanabi import Hanabi
import numpy as np
from player.playsleft import PlaysLeftPlayer

n_trials = 100
scores = np.zeros((n_trials, ), dtype=int)
for nn in range(n_trials):
    h = Hanabi(4, PlaysLeftPlayer)
    scores[nn] = h.play()

print(np.mean(scores))
print(np.max(scores))
