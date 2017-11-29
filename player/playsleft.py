import player.clues

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
