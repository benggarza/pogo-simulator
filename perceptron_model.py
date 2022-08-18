from player_model import PlayerModel
from random_model import RandomModel
import tensorflow as tf
from keras import Sequential
from keras.layers import Dense
from random import random
import pandas as pd

# A simple reward-based perceptron model
class PerceptronModel(PlayerModel):
    def __init___(self, epsilon=0.2):
        # Hot-encoded: index 0 = No Switch, index 1 = Yes Switch
        self.decide_switch_model = self.build_model()
        # index 0 = option A, index 1 = option B
        self.choose_switch_model = self.build_model()
        # index 0 = wait, index 1 = attack
        self.wait_or_attack_model = self.build_model()
        # index 0 = fast, index 1 = charged
        self.fast_or_charged_model = self.build_model()
        # index 0 = option A, index 1 = option B
        self.choose_charged_move_model = self.build_model()
        # index 0 = No shield, index 1 = Yes shield
        self.decide_shield_model = self.build_model()
        self.random_model = RandomModel()

    def build_model(self):
        model = Sequential()
        model.add(Dense(16))
        model.add(Dense(2))
        return model

    def train(self, battle_state_history: pd.Series, battle_action_history: pd.Series):
        for state_history, action_history in zip(battle_state_history.to_list(), battle_action_history.to_list()):
            state_history_df = pd.DataFrame(state_history)
            action_history_df = pd.DataFrame(action_history)

            # Calculate rewards at each turn TODO
            reward = {}


        return None

    # returns true or false to use switch
    def decide_switch(self, state):
        if random() < self.epsilon:
            return self.random_model.decide_switch(state)
        else:
            decision = self.decide_switch_model.predict([state])
            return False if decision==0 else True

    # returns team index of chosen party pokemon
    def choose_switch(self, state, party_a, party_b):
        if random() < self.epsilon:
            return self.random_model.choose_switch(state, party_a, party_b)
        else:
            decision = self.choose_switch_model.predict([state])
            return party_a.get_team_index() if decision==0 else party_b.get_team_index()

    # returns 'wait' or 'attack'
    def wait_or_attack(self, state):
        if random() < self.epsilon:
            return self.random_model.wait_or_attack(state)
        else:
            decision = self.wait_or_attack_model.predict([state])
            return 'wait' if decision==0 else 'attack'

    # returns 'fast' or 'charged'
    def fast_or_charged(self, state):
        if random() < self.epsilon:
            return self.random_model.fast_or_charged(state)
        else:
            decision = self.fast_or_charged_model.predict([state])
            return 'fast' if decision==0 else 'charged'

    # returns 'a' or 'b'
    def choose_charged_move(self, state, charged_a, charged_b):
        if random() < self.epsilon:
            return self.random_model.choose_charged_move(state, charged_a, charged_b)
        else:
            decision = self.choose_charged_move_model.predict([state])
            return 'a' if decision==0 else 'b'

    # returns True or False to use shield
    def decide_shield(self, state):
        if random() < self.epsilon:
            return self.random_model.decide_shield(state)
        else:
            decision = self.decide_shield_model.predict([state])
            return False if decision==0 else True

    def format_state(self, state):
        # TODO
        return None

    def flatten_dict(self, dict):
        # TODO
        return None