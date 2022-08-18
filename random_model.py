from player_model import PlayerModel
from random import random

## The simplest model, doing things randomly
class RandomModel(PlayerModel):
    def __init__(self):
        self.switch_rate = 0.2
        self.charged_rate = 0.6
        self.shield_rate = 0.8

    def load_model(self):
        pass
    def build_model(self):
        pass
    def train(self, state_history, action_history):
        pass
    def decide_switch(self, state):
        return True if random() < self.switch_rate else False
    def choose_switch(self, state, party_a, party_b):
        return party_a.get_team_index() if random() < 0.5 else party_b.get_team_index()
    def wait_or_attack(self, state):
        return "attack"
    def fast_or_charged(self, state):
        return "charged" if random() < self.charged_rate else "fast"
    def choose_charged_move(self, state, charged_a, charged_b):
        return "a" if random() < 0.5 else "b"
    def decide_shield(self, state):
        return True if random() < self.shield_rate else False

    def __str__(self):
        return "random"
    
    