import player.clues


class PlaysLeftPlayer:
    def __init__(self, player_idx, info):
        self.n_heldcards = info.n_heldcards
        self.player_idx = player_idx
        self.last_idx_played = -1
        return

    def play_turn(self, info):
        self.last_idx_played = 0
        action = ('play', (self.last_idx_played, ))
        self.n_heldcards -= 1
        return action

    def get_card(self):
        self.n_heldcards += 1
        return 0

    def get_clue(self, clue):
        return
