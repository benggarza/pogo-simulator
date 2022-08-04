from player import Player
from pokemon import Pokemon

from math import floor
from random import random
from copy import deepcopy
from json import dumps


class Battle:
    def __init__(self, gm):
        self.gm = gm

        self.turn = 1
        self.timer = 0
        self.players={'a': None,'b': None}
        self.leads={'a': None, 'b': None}
        self.phase= "neutral"
        self.state={}
        self.state_history = []
        self.action_history = []
        self.verbose = True

    def add_players(self, player_a, player_b):
        if player_a.team_empty():
            raise Exception("Error: Player A's team is not set, cannot be added to Battle")
        if player_b.team_empty():
            raise Exception("Error: Player B's team is not set, cannot be added to Battle")
        player_a.set_opponent(player_b)
        player_a.set_player('a')
        self.players['a'] = player_a
        self.leads['a'] = player_a.get_lead()
        player_b.set_opponent(player_a)
        self.players['b'] = player_b
        player_b.set_player('b')
        self.leads['b'] = player_b.get_lead()

    def run(self):
        for player in self.players.values():
            player.reset_stats()
            for p in player.team:
                p.reset_stats()

        print("Starting battle!")
        # Prepare turn 1 state
        self.update_state()
        self.record_state()
        if self.verbose:
            self.print_battle_state()
        
        # simulation starts here
        while self.turn <= 480:
            # reduce timer
            self.timer = max(self.timer-0.5, 0)

            # reduce cooldown for each pokemon
            for poke in self.leads.values():
                poke.decrease_cooldown()

            # reduce switch timer for each player
            for player in self.players.values():
                player.decrease_switch_timer()
            
            ### if self.phase == "neutral": # we are not implemented battle phases at the moment
            result = self.step()
            if result is not None:
                return result
        return self.end_game()

    # Process one turn of a battle
    def step(self):

        # Check if game is over
        if self.turn > 480:
            raise Exception("Error: attempted to execute turn past 480")

        # don't process actions if not in neutral battle phase
        if self.phase!="neutral":
            raise Exception('Error: attempted to process a turn of battle in a not neutral game state')
        
        # Get player actions
        action_queue = []
        for player in self.players.values():
            action_queue.append(player.get_action(self.state))
        
        # Check validity of each action and evaluate priority
        for action in action_queue:
            action_turn = action['turn']
            action_player = self.players[action['player']]
            action_type = action['type']
            action_arg = action['arg']
            if action_type == "fast":
                prev_action = action_player.get_prev_action()['type']
                if prev_action == "fast":
                    if self.turn - action_turn >= action_player.get_lead().get_fast_move()['cooldown'] - 1:
                        print(f"Action waiting for {self.turn - action_turn} turns")
                        print(f"Required wait time {action_player.get_lead().get_fast_move()['cooldown'] - 1}")
                        action['priority'] += 20
                    else:
                        action_queue.remove(action)
                if prev_action == "charged":
                    if self.turn - action_turn >= 1:
                        action['priority'] += 20
                    else:
                        action_queue.remove(action)
                # TODO remove fast move if not valid
            elif action_type == "charged":
                attacker = action_player.get_lead()
                if attacker.get_energy() < attacker.get_charged_move(action_arg)['energy_cost']:
                    action_queue.remove(action)
            elif action_type == "switch":
                if action_player.get_switch_timer() > 0:
                    action_queue.remove(action)
                
        # Sort actions based on priority
        action_queue.sort(key=lambda action: action['priority'], reverse=True)

        # Execute actions in priority order
        for action in action_queue:
            self.execute_action(action)
            self.record_action(action)
            # TODO don't execute charged move if a priority move faints opposing pokemon
            # right now will cancel any action
            defender_lead = self.players[action['player']].get_opponent().get_lead()
            if action['priority'] > 0 and defender_lead.fainted():
                action_queue = []
                break
            # Clear all other actions after a charged move
            if action['type'] == 'charged':
                action_queue = []
                break

        # Check if a pokemon fainted
        fainted = False
        for (poke, player) in zip(self.leads.values(), self.players.values()):
            if poke.fainted():
                print(f"Player {player.get_player()}'s pokemon {player.get_lead().get_name()} fainted")
                fainted = True

        if fainted:
            # Check if a player is out of pokemon
            for player in self.players.values():
                if player.get_num_remaining_pokemon() == 0:
                    return self.end_game()

            # Check if a force switch is needed
            for (poke, player) in zip(self.leads.values(), self.players.values()):
                if poke.fainted():
                    self.force_switch(player)

        # Increment turn
        self.turn += 1

        # Add state to memory
        self.update_state()
        self.record_state()
        if self.verbose:
            self.print_battle_state()

        return None

        
    def force_switch(self, player):
        if player.get_num_remaining_pokemon() == 0:
            raise Exception("Error: Battle entered force switch on player with zero party pokemon left")
        switch_poke = None
        if player.get_num_remaining_pokemon() == 2:
            switch_poke = player.choose_force_switch(self.state)
        else:
            party = player.get_party()
            if party[0].fainted():
                switch_poke = party[1]
            else:
                switch_poke = party[0]
        player.swap_lead(switch_poke)
        print(f"Player {player.get_player()} switches in {player.get_lead().get_name()}")

    def execute_action(self, action):
        action_type = action['type']
        player = self.players[action['player']]
        opponent = player.get_opponent()
        attacker = player.get_lead()
        defender = opponent.get_lead()

        message = f"Player {player.player_label} "

        if action_type == 'switch':
            switch_poke = player.get_team()[action['arg']]
            player.get_lead().reset_boosts()
            player.swap_lead(switch_poke)
            self.leads[player.player_label] = switch_poke
            player.start_switch_timer()

            message += f"switches in {switch_poke.name}"
        elif action_type =='fast' or action_type == 'charged':
            move = None
            energy_delta = 0
            shield = False
            if action_type == 'fast':
                move = attacker.get_fast_move()
                energy_delta = move['energy_gain']
            if action_type == 'charged':
                move = attacker.get_charged_move(action['arg'])
                energy_delta = -1*move['energy_cost']
                if opponent.get_shields() > 0:
                    shield = opponent.decide_shield(self.state)
            boosted_atk_stat = attacker.get_boosted_atk()
            boosted_def_stat = defender.get_boosted_def()
            stab = 1.2 if attacker.get_fast_move()['type'] in attacker.types else 1.0
            effectiveness = 1.0
            for type in defender.types:
                if type is not None:
                    effectiveness *= self.gm.get_type_effectiveness(move['type'], type)
            damage = floor(0.5 * move['power'] * (boosted_atk_stat/boosted_def_stat) * stab * effectiveness) + 1

            message += f"{attacker.name} uses {action_type} move {move['name']}"

            if not shield:
                defender.deal_damage(damage)
                message += f", deals {damage} damage"
            else:
                opponent.use_shield()
                message += f", player {opponent.get_player()} uses shield"
            attacker.add_energy(energy_delta)

            # calculate buffs/debuffs
            if 'attacker_atk_boost' in move.keys() and random() < move['attacker_atk_boost_chance']:
                attacker.boost_atk(move['attacker_atk_boost'])
            if 'attacker_def_boost' in move.keys() and random() < move['attacker_def_boost_chance']:
                attacker.boost_def(move['attacker_def_boost'])

            if 'defender_atk_boost' in move.keys() and random() < move['defender_atk_boost_chance']:
                defender.boost_atk(move['defender_atk_boost'])
            if 'defender_def_boost' in move.keys() and random() < move['defender_def_boost_chance']:
                defender.boost_def(move['defender_def_boost'])

            # reset cooldown
            if action_type=='fast':
                attacker.start_cooldown()
            
             
        else: # action is wait
            message += f"waits"


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
        history = {'state': self.state_history, 'action': self.action_history, 'winner': 'tie', 'win_margin': 0}
        player_a = self.players['a']
        player_b = self.players['b']
        a_remaining = player_a.get_num_remaining_pokemon()
        b_remaining = player_b.get_num_remaining_pokemon()
        if a_remaining > 0 and b_remaining == 0:
            history['winner'] = 'A'
            for p in player_a.get_team():
                history['win_margin'] += p.get_hp()
        elif b_remaining > 0 and a_remaining == 0:
            history['winner'] = 'B'
            for p in player_b.get_team():
                history['win_margin'] += p.get_hp()

        return history


                
    def update_state(self):
        self.state['turn'] = self.turn
        self.state['player_a'] = self.players['a'].state_dict()
        self.state['player_b'] = self.players['b'].state_dict()

    def record_state(self):
        self.state_history.append(deepcopy(self.state))

    def print_battle_state(self):
        print("\nTurn: ", self.turn)
        player_a = self.players['a']
        player_b = self.players['b']
        print(player_a)
        print(f"Lead Pokemon: {player_a.get_lead()}")
        print(player_b)
        print(f"Lead Pokemon: {player_b.get_lead()}")