class Player:
    def __init__(self):
        self.player_label = ""

        self.team_builder = None
        self.player_model = None
        self.opponent = None

        self.team = []
        self.lead_index = -1

        self.prev_action = {'type': None, 'turn': 0}
        self.switch_timer = 0
        self.shields = 2

    def set_team_builder(self, tb):
        self.team_builder = tb

    def set_player_model(self, m):
        self.player_model = m

    def set_opponent(self, o):
        self.opponent = o

    def get_opponent(self):
        return self.opponent

    def team_empty(self):
        return len(self.team) == 0

    def set_player(self, player_label):
        self.player_label = player_label

    def get_player(self):
        return self.player_label

    def choose_team(self, cup):
        self.team = self.team_builder.choose_team(cup)
        self.lead_index = 0
        for i in range(3):
            self.team[i].set_team_index(i)
        return self.team

    def get_team(self):
        return self.team

    def get_lead(self):
        return self.team[self.lead_index]

    def get_party(self):
        return [p for p in self.team if p.team_index != self.lead_index]

    def get_num_remaining_pokemon(self):
        return 3 - len([p for p in self.team if p.fainted()])

    def reset_stats(self):
        self.prev_action = {'type': None, 'turn': 0}
        self.switch_timer = 0
        self.shields = 2

    def get_switch_timer(self):
        return self.switch_timer

    def start_switch_timer(self):
        self.switch_timer = 30

    def decrease_switch_timer(self, time = 0.5):
        self.switch_timer = max(0, self.switch_timer - time)

    def get_action(self, state):

        action = {'turn': state['turn'], 'player': self.player_label, 'type': None, 'arg': None, 'priority': 0}

        ### can we switch, and do we want to switch?
        if (self.switch_timer == 0 and self.get_num_remaining_pokemon() > 1) and self.player_model.decide_switch(state):
            action['type']='switch'

            # if we have two options, choose an option
            if self.get_num_remaining_pokemon() == 3:
                party = self.get_party()
                action['arg'] = self.player_model.choose_switch(state, party[0], party[1])

            # otherwise we just have one option
            else: # remaining pokemon is 2
                action['arg'] = self.get_party()[0].get_team_index()
            return action

        ### do we wait?
        if self.player_model.wait_or_attack(state) == 'wait':
            action['type'] = 'wait'
            return action
        
        ### otherwise we attack
        # do we want to use a fast move, or is that our only option
        charged_moves_ready = self.team[self.lead_index].get_ready_charged()
        if len(charged_moves_ready) == 0 or self.player_model.fast_or_charged(state) == 'fast':
            action['type'] = 'fast'
            return action

        ### otherwise use a charged attack
        action['type'] = 'charged'
        if len(charged_moves_ready) == 1:
            action['arg'] = charged_moves_ready[0]['charged_move_label']
        else: # we need to choose between both options
            action['arg'] = self.player_model.choose_charged_move(state, charged_moves_ready['a'], charged_moves_ready['b'])
        return action

    def choose_force_switch(self, state):
        if self.get_num_remaining_pokemon() != 2:
            raise Exception("Error: choose_force_switch was called with player not having two switch options")
        party = self.get_party()
        return  self.team[self.player_model.choose_switch(state, party[0], party[1])]


    def set_prev_action(self, prev_action):
        self.prev_action = prev_action

    def get_prev_action(self):
        return self.prev_action

    def swap_lead(self, p):
        self.lead_index = p.get_team_index()

    def get_shields(self):
        return self.shields

    def decide_shield(self, state):
        if self.shields <= 0:
            raise Exception("Error: Battle asked Player with no shields to decide shield")
        return self.player_model.decide_shield(state)

    def use_shield(self):
        if self.shields <= 0:
            raise Exception("Error: Attempted to use shield with no shields remaining")
        self.shields = max(0, self.shields - 1)

    def state_dict(self):
        state = {}
        state['shields'] = self.get_shields()
        state['switch_timer'] = self.get_switch_timer()
        state['num_remaining'] = self.get_num_remaining_pokemon()
        state['lead_pokemon'] = self.get_lead().state_dict()
        state['party_poke_a'] = self.get_party()[0].state_dict()
        state['party_poke_b'] = self.get_party()[1].state_dict()
        return state

    def __str__(self):
        s = f"Player {self.player_label} | model {self.player_model}"
        s += f" | Remaining Pokemon: {self.get_num_remaining_pokemon()} | Shields: {self.get_shields()}"
        s += f" | Switch Timer: {self.get_switch_timer()}"
        return s