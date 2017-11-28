from hanabi import Hanabi
import numpy as np


class PlaysLeftPlayer:
    def __init__(self, player_idx):
        self.player_idx = player_idx
        self.last_idx_played = -1
        return

    def play_card(self):
        self.last_idx_played = 0
        return self.last_idx_played

    def get_card(self):
        return 0


n_trials = 10000
scores = np.zeros((n_trials, ), dtype=int)
for nn in range(n_trials):
    h = Hanabi([PlaysLeftPlayer(player_idx) for player_idx in range(4)])
    scores[nn] = h.play()

print(np.mean(scores))
print(np.max(scores))
