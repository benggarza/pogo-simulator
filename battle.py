from player import Player
from pokemon import Pokemon

from math import floor
from random import random
from copy import deepcopy


class Battle:
    def __init__(self, gm, verbose=False):
        self.gm = gm

        self.turn = 0
        self.timer = 0
        self.players={'a': None,'b': None}
        self.leads={'a': None, 'b': None}
        self.phase= "neutral"
        self.action_queue = []
        self.state={}
        self.state_history = []
        self.action_history = []
        self.verbose = verbose

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
        # simulation starts here
        while self.turn <= 480:
            # increase timer
            self.timer += 0.5

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

        # Increment turn
        self.turn += 1

        # Add state to memory
        self.update_state()
        self.record_state()
        if self.verbose:
            self.print_battle_state()

        # Check if game is over
        if self.turn > 480:
            raise Exception("Error: attempted to execute turn past 480")

        # don't process actions if not in neutral battle phase
        if self.phase!="neutral":
            raise Exception('Error: attempted to process a turn of battle in a not neutral game state')
        
        # Get player actions
        # Indicate if a charged move is queued
        for player in self.players.values():
            if player.get_lead().get_cooldown() == 0:
                action = player.get_action(self.state)
                self.action_queue.append(action)

        turn_action_queue = []
        charged_move_this_turn = {'a': False, 'b': False}
        # Check validity of each action and evaluate priority
        # Indicate if a charged move will be used this turn for CMP
        self.log(f"\tstep(), turn {self.turn}: PROCESSING QUEUED ACTIONS")
        action_i = 0
        while action_i < len(self.action_queue):
            action = self.action_queue[action_i]
            action_turn = action['turn']
            action_player = self.players[action['player']]
            action_type = action['type']
            action_arg = action['arg']
            action_poke = action_player.get_team()[action['pokemon']]
            self.log(f"\tstep(), turn {self.turn}: processing queued action: {self.action_str(action)}")

            valid = False
            remove = False
            # if player attempting to queue a move with a current cooldown, remove the action
            if action_turn == self.turn and action_poke.get_cooldown() > 0:
                    self.log(f"\tstep(), turn {self.turn}: removing action {self.action_str(action)} because pokemon {action_poke.get_name()} cooldown is non-zero")
                    remove = True
            # fast move becomes "valid" when it is time to deal damage
            elif action_type == "fast":
                prev_action = action_player.get_prev_action()['type']
                # If player attempting to queue a move with no cooldown, then "start" the move by starting the cooldown
                if action_turn == self.turn and action_poke.get_cooldown() == 0:
                    action_poke.start_cooldown()
                # if pokemon cooldown is 1, then fast move can now deal damage     
                if action_poke.get_cooldown() == 1:
                    valid = True
                    action['priority'] += 20
                    self.log(f"\tstep(), turn {self.turn}: Action {self.action_str(action)} given higher priority for waiting the required time to pass")
                
            elif action_type == "charged":
                if action_poke.get_energy() < action_poke.get_charged_move(action_arg)['energy_cost']:
                    self.log(f"\tstep(), turn {self.turn}: removing action {self.action_str(action)} because pokemon {attacker.get_name()} (energy {attacker.get_energy()}) doesn't have enough energy for charged move {attacker.get_charged_move(action_arg)['name']}")
                    remove = True
                else:
                    # CMP Calculation
                    charged_move_this_turn[action_player.get_player()] = True
                    attacker = self.leads[action_player.get_player()]
                    defender = self.leads[action_player.get_opponent().get_player()]
                    if charged_move_this_turn[action_player.get_opponent().get_player()]:
                        if attacker.get_boosted_atk() > defender.get_boosted_atk():
                            self.log(f"\tstep(), turn {self.turn}: CMP goes to {attacker.get_name()}")
                            action['priority'] += 10
                        elif attacker.get_boosted_atk() < defender.get_boosted_atk():
                            self.log(f"\tstep(), turn {self.turn}: CMP goes to {defender.get_name()}")
                            action['priority'] -= 10
                    valid = True
            # does a switch get priority over charged moves? for now assume switches happen last
            elif action_type == "switch":
                if action_player.get_switch_timer() > 0:
                    self.log(f"\tstep(), turn {self.turn}: removing action {self.action_str(action)} because player {action_player.get_player()}'s switch timer is on")
                    remove = True
                else:
                    valid = True
                    action['priority'] -= 20
            elif action_type == "wait":
                valid = True

            if valid:
                turn_action_queue.append(action)
                self.action_queue.remove(action)
            elif remove:
                self.action_queue.remove(action)
            else:
                action_i += 1

                
        # Sort actions based on priority
        turn_action_queue.sort(key=lambda action: action['priority'], reverse=True)

        # Execute actions in priority order
        charged_move_executed = {'a': False, 'b': False}
        priority_move_used = {'a': 0, 'b': 0}
        self.log(f"\tstep(), turn {self.turn}: PROCESSING TURN ACTIONS")
        while len(turn_action_queue) > 0:
            # Dequeue action from queue
            action = turn_action_queue[0]
            turn_action_queue.remove(action)
            self.log(f"\tstep(), turn {self.turn}: processing turn action {self.action_str(action)}")

            action_turn = action['turn']
            action_player = self.players[action['player']]
            action_attacker = action_player.get_lead()
            action_defender = action_player.get_opponent().get_lead()
            action_type = action['type']
            action_arg = action['arg']

            valid = True

            # Runtime conditions to invalidate a processed move
            if action_type == 'fast':
                # Don't beat a dead horse
                if action_defender.fainted():
                    self.log(f"\tstep(), turn {self.turn}: Action  not being executed because opponent is already fainted")
                    valid = False
                # pokemon don't get to sneak in a fast move if a charged move faints them
                elif True in charged_move_executed.values() and action_attacker.fainted():
                    self.log(f"\tstep(), turn {self.turn}: Action {self.action_str(action)} not being executed because pokemon was fainted by a charged move")
                    valid = False
                # higher priority fast moves have the opportunity to faint a pokemon before they receive damage
                elif priority_move_used[action_player.get_opponent().get_player()] > action['priority'] and action_attacker.fainted():
                    self.log(f"\tstep(), turn {self.turn}: Action {self.action_str(action)} not being executed because pokemon was fainted by a higher priority fast move")
                    valid = False
                else:
                # record the priority of the fast move executed for future moves to reference
                    priority_move_used[action['player']] = action['priority']
            elif action_type =='charged':
                # only one charged move per turn
                if True in charged_move_executed.values():
                    self.log(f"\tstep(), turn {self.turn}: Action {self.action_str(action)} not being executed because a previous charged move was executed")
                    valid = False
                else:
                    charged_move_executed[action['player']] = True

            if action['pokemon'] != action_attacker.get_team_index():
                self.log(f"\tstep(), turn {self.turn}: Action {self.action_str(action)} not being executed because lead has changed since action was queued")
                valid = False

            if valid:
                self.log(f"\tstep(), turn {self.turn}: Executing {self.action_str(action)}")
                self.execute_action(action)
                self.record_action(action)

        # Check if a pokemon fainted
        fainted = False
        for (poke, player) in zip(self.leads.values(), self.players.values()):
            self.log(f"\tstep(), turn {self.turn}: {poke.get_name()}: {poke.get_hp()}")
            if poke.fainted():
                self.log(f"Player {player.get_player()}'s pokemon {poke.get_name()} fainted")
                fainted = True

        if fainted:
            # Check if a player is out of pokemon
            for player in self.players.values():
                if player.get_num_remaining_pokemon() == 0:
                    return self.end_game()

            # Check if a force switch is needed
            for (poke, player) in zip(self.leads.values(), self.players.values()):
                if poke.fainted():
                    self.log(f"\tstep(), turn {self.turn}: forcing player {player.get_player()} to switch")
                    self.force_switch(player)
                    # if we do a force switch, completely reset the action queue
                    self.action_queue = []

        return None

        
    def force_switch(self, player):
        self.log(f"\tforce_switch(), turn {self.turn}: player has {player.get_num_remaining_pokemon()} pokes left")
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
        self.leads[player.get_player()] = player.get_lead()
        self.log(f"Player {player.get_player()} switches in {switch_poke.get_name()} with {switch_poke.get_hp()} hp")

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
            # remove all player's queued actions after a switch
            for a in self.action_queue:
                if a['player'] == action['player'] and a['pokemon'] != switch_poke.get_team_index():
                    self.log(f"\texecute_action(), turn {self.turn}: removing action {self.action_str(a)} after a switch")
                    self.action_queue.remove(a)

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
            stab = 1.2 if attacker.get_fast_move()['type'] in attacker.get_types() else 1.0
            effectiveness = 1.0
            for type in defender.get_types():
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
            if action_type == 'charged':
                attacker.decrease_cooldown(turns=attacker.get_cooldown())
                defender.decrease_cooldown(turns=defender.get_cooldown())
            
             
        else: # action is wait
            message += f"waits"


        player.set_prev_action(action)
        self.log(message)

    def record_action(self, action):
        self.action_history.append(deepcopy(action))

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

    def log(self, stmt):
        if self.verbose:
            print(stmt)
        
    def action_str(self, action):
        s = f"(T{action['turn']}, pri{action['priority']}, P{action['player']}, p{action['pokemon']}, {action['type']}"
        if action['arg'] is not None:
            s += f"{action['arg']}"
        s += ")"
        return s

    def print_battle_state(self):
        self.log(f"\nTurn: {self.turn}")
        player_a = self.players['a']
        player_b = self.players['b']
        self.log(player_a)
        self.log(f"Lead Pokemon: {player_a.get_lead()}")
        self.log(player_b)
        self.log(f"Lead Pokemon: {player_b.get_lead()}")