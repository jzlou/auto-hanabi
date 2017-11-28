from hanabi import Hanabi


class PlaysLeftPlayer:
    def __init__(self, player_idx):
        self.player_idx = player_idx
        return

    def play_card(self):
        return 0


h = Hanabi([PlaysLeftPlayer(player_idx) for player_idx in range(4)])
