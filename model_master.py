from math import inf
from battle_engine import BattleEngine
from player import Player
from random import randint
import pandas as pd
from os.path import exists
class ModelMaster:
    def __init__(self, gm, team_builder_a, model_a, team_builder_b, model_b, max_battles, training_interval=5, verbose=False, train=False):
        self.gm = gm
        self.battle_engine = BattleEngine(self.gm, verbose=verbose)
        self.player_a = Player()
        self.player_b = Player()
        self.model_a = model_a
        self.model_b = model_b
        self.team_builder_a = team_builder_a
        self.team_builder_b = team_builder_b
        self.player_a.set_player_model(model_a)
        self.player_b.set_player_model(model_b)
        self.player_a.set_team_builder(team_builder_a)
        self.player_b.set_team_builder(team_builder_b)
        self.record = {'A': 0, 'B': 0, 'tie': 0}

        self.max_battles = max_battles
        self.training_interval = training_interval
        self.train = train

        self.state_history = []
        self.action_history = []

    def run(self):
        battle_num = 1
        # TODO include condition to check if models are plateauing
        while battle_num <= self.max_battles:
            # randomly choose cup
            cup = [{'name': "Great", 'cp': 1500}, {'name': "Ultra", 'cp': 2500}, {'name': "Master", 'cp': inf}][randint(0,2)]
            print(f"Playing in {cup['name']} league")

            # Choose teams
            self.player_a.choose_team(cup)
            self.player_b.choose_team(cup)

            # Create battle
            b = self.battle_engine.new_battle(self.player_a, self.player_b, cup)

            # Run simulation
            history = b.run()

            # Add battle results to histories
            self.state_history.append(history['state'])
            self.action_history.append(history['action'])
            self.record[history['winner']] += 1

            # At given interval, train models on new history data and save history data to file
            if battle_num % self.training_interval == 0:
                if self.train:
                    self.model_a.train((self.state_history, self.action_history))
                    self.model_b.train((self.state_history, self.action_history))
                self.write_history()
            
            print(f"Player {history['winner']} wins by a margin of {history['win_margin']}")
            battle_num += 1

        print('Finished simulating')
        print(f"After {battle_num-1} battles, player A has {self.record['A']} wins, and player B has {self.record['B']} wins")

        # Save any leftover data
        self.write_history()

    def write_history(self):
        if exists('state_history.json'):
            state_history_df = pd.concat([pd.read_json('state_history.json', typ='series', orient='records'), pd.Series(self.state_history)], ignore_index=True)
        else:
            state_history_df = pd.Series(self.state_history)
        state_history_df.to_json("state_history.json")
        if exists('action_history.json'):
            action_history_df = pd.concat([pd.read_json('action_history.json', typ='series', orient='records'), pd.Series(self.action_history)], ignore_index=True)
        else:
            action_history_df = pd.Series(self.action_history)
        action_history_df.to_json("action_history.json")
        self.state_history = []
        self.action_history = []
