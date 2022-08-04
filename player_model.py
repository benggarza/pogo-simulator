### Pseudo-Interface for Player Models

class PlayerModel:

    def load_model(self):
        raise NotImplementedError("Error: load_model not implemented for this model")

    def build_model(self):
        raise NotImplementedError("Error: build_model not implemented for this model")

    def train(self, data):
        raise NotImplementedError("Error: train not implemented for this model")

    def decide_switch(self, state):
        raise NotImplementedError("Error: decide_switch not implemented for this model")

    def choose_switch(self, state, party_a, party_b):
        raise NotImplementedError("Error: choose_switch not implemented for this model")

    def wait_or_attack(self, state):
        raise NotImplementedError("Error: wait_or_attack not implemented for this model")

    def fast_or_charged(self, state):
        raise NotImplementedError("Error: fast_or_charged not implemented for this model")

    def choose_charged_move(self, state, charged_a, charged_b):
        raise NotImplementedError("Error: choose_charged_move not implemented for this model")

    def decide_shield(self, state):
        raise NotImplementedError("Error: decide_shield not implemented for this model")

    def __str__(self):
        raise NotImplementedError("Error: string method not implemented for this model")