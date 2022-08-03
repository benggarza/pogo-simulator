import helpers
from player import Player
from pokemon import Pokemon

from math import floor
from random import random
from copy import deepcopy
from json import dumps


class Battle:
    def __init__():
        turn = 0
        timer = 0
        players={'a': None,'b': None}
        leads={'a': None, 'b': None}
        phase= "neutral"
        state={}
        state_history = []
        action_history = []
        verbose = True

    def add_players(self, player_a, player_b):
        if player_a.team_empty():
            raise Exception("Error: Player A's team is not set, cannot be added to Battle")
        if player_b.team_empty():
            raise Exception("Error: Player B's team is not set, cannot be added to Battle")
        player_a.set_opponent(player_b)
        self.players['a'] = player_a
        self.leads['a'] = player_a.get_lead()
        player_b.set_opponent(player_a)
        self.players['b'] = player_b
        self.leads['b'] = player_b.get_lead()

    def run(self):
        for player in self.players:
            player.reset_stats()
            for p in player.team:
                p.reset_stats()

        # Prepare turn 1 state
        self.update_state()
        self.record_state()
        if self.verbose:
            self.print_battle_state()

        # simulation starts here
        while self.turn <= 480:
            # reduce cooldown for each pokemon
            for poke in self.pokes:
                poke.decrease_cooldown()

            # reduce switch timer for each player
            for player in self.players:
                player.decrease_switch_timer()
            
            ### if self.phase == "neutral": # we are not implemented battle phases at the moment
            self.turn()
        self.end_game()

    # Process one turn of a battle
    def turn(self):

        # Check if game is over
        if self.turn > 480:
            raise Exception("Error: attempted to execute turn past 480")

        # don't process actions if not in neutral battle phase
        if self.phase!="neutral":
            raise Exception('Error: attempted to process a turn of battle in a not neutral game state')
        
        # Get player actions
        action_queue = []
        for player in self.players:
            action_queue.append(player.get_action(self.state))
        
        # Check validity of each action and evaluate priority
        for action in action_queue:
            action_turn = action['turn']
            action_player = action['player']
            action_type = action['type']
            action_arg = action['arg']
            if action_type == "fast":
                prev_action = action_player.get_prev_action()
                if prev_action == "fast":
                    if self.turn - action_turn >= action_player.get_lead().get_fast_move()['cooldown'] - 1:
                        action['priority'] += 20
                    else:
                        action_queue.remove(action)
                if prev_action == "charged":
                    if self.turn - action.turn >= 1:
                        action['priority'] += 20
                    else:
                        action_queue.remove(action)
                # TODO remove fast move if not valid
            elif action_type == "charged":
                if action_player.get_lead().get_energy() < action_arg['energy_cost']:
                    action_queue.remove(action)
            elif action_type == "switch":
                if action_player.get_switch_timer() > 0:
                    action_queue.remove(action)
                
        # Sort actions based on priority
        action_queue.sort(key=lambda action: action['priority'], reverse=True)

        # Execute actions in priority order
        # TODO don't execute charged move if a priority move faints opposing pokemon
        for action in action_queue:
            self.execute_action(action)
            self.record_action(action)

        # Check for fainted pokemon
        for (poke, player) in zip(self.pokes, self.players):
            if poke.fainted():
                if player.get_num_remaining_pokemon() == 0:
                    return self.end_game()
                else:
                    self.force_switch(player)

        # Add state to memory
        self.update_state()
        self.record_state()
        if self.verbose:
            self.print_battle_state()

        # Increment turn
        self.turn += 1

        
    def force_switch(self, player):
        if player.get_num_remaining_pokemon() == 1:
            switch_poke = player.get_party()

    def execute_action(self, action):
        action_type = action['type']
        player = action['player']
        opponent = player.get_opponent()
        attacker = player.lead
        defender = opponent.lead

        message = "Player " + player.player_label + " "

        if action_type == 'switch':
            switch_poke = action['arg']
            player.get_lead().reset_boosts()
            player.swap_lead(switch_poke)
            self.leads[player.player_label] = switch_poke
            player.start_switch_timer()

            message += "switches in " + switch_poke.name

        elif action_type =='fast' or action_type == 'charged':
            move = None
            energy_delta = 0
            shield = False
            if action_type == 'fast':
                move = attacker.fast_move
                energy_delta = move['energy_gain']
            if action_type == 'charged':
                move = action['arg']
                energy_delta = move['energy_cost']
                if opponent.get_shields() > 0:
                    shield = opponent.decide_shield(self.state)
            boosted_atk_stat = attacker.get_boosted_atk()
            boosted_def_stat = defender.get_boosted_def()
            stab = 1.2 if attacker.get_fast_move()['type'] in attacker.types else 1.0
            effectiveness = helpers.get_effectiveness(move['type'], defender.types)
            damage = floor(0.5 * attacker.get_fast_move()['power'] * (boosted_atk_stat/boosted_def_stat) * stab * effectiveness) + 1

            if not shield:
                defender.deal_damage(damage)
            else:
                defender.use_shield()
            attacker.add_energy(energy_delta)

            # calculate buffs/debuffs
            if move['attacker_atk_boost'] and random() < move['attacker_atk_boost_chance']:
                attacker.boost_atk(move['attacker_atk_boost'])
            if move['attacker_def_boost'] and random() < move['attacker_def_boost_chance']:
                attacker.boost_def(move['attacker_def_boost'])

            if move['defender_atk_boost'] and random() < move['defender_atk_boost_chance']:
                defender.boost_atk(move['defender_atk_boost'])
            if move['defender_def_boost'] and random() < move['defender_def_boost_chance']:
                defender.boost_def(move['defender_def_boost'])

            # reset cooldown
            if action_type=='fast':
                attacker.start_cooldown()
            
            message += attacker.name + "uses " + action_type + " move " + move['name'], "deals " + damage + " damage"
        else: # action is wait
            message += "waits"


        player.set_prev_action(action)
        if self.verbose:
            print(message)

    def record_action(self, action):
        self.action_history.append(deepcopy(action))
    
    def save_action_history(self, filename='action_history.json'):
        with open(filename, 'a') as f:
            f.write(dumps(self.action_history))

    def end_game(self):
        # record final game state
        self.update_state()
        self.record_state()

        # save history to files
        self.save_action_history()
        self.save_state_history()
                
    def update_state(self):
        self.state['turn'] = self.turn
        self.state['player_a'] = self.players['a'].state_dict()
        self.state['player_b'] = self.players['b'].state_dict()

    def record_state(self):
        self.state_history.append(deepcopy(self.state))

    def save_state_history(self, filename='state_history.json'):
        with open(filename, 'a') as f:
            f.write(dumps(self.state_history))

    def print_battle_state(self):
        print("Turn: ", self.turn)
        player_a = self.players['a']
        player_b = self.players['b']
        print(player_a)
        print("\tLead Pokemon:\n", player_a.get_lead())
        print(player_b)
        print("\tLead Pokemon:\n" + player_b.get_lead())