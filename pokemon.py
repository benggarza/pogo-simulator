from math import floor
class Pokemon:
    def __init__(self, pokemon_id, name, types, base_atk, base_def, base_sta):
        self.team_index = -1
        self.player=None

        self.types = types

        self.name = name
        self.pokemon_id = pokemon_id
        self.level = 1
        self.cpm = 0.094
        self.atk_iv = 0
        self.def_iv = 0
        self.sta_iv = 0
        self.base_atk = base_atk
        self.base_def = base_def
        self.base_sta = base_sta
        self.atk_stat = 0
        self.def_stat = 0
        self.sta_stat = 0 # same as to full HP
        self.shadow = False

        self.cp = 0
        self.fast_move = None
        self.charged_moves = {'a': None, 'b': None}

        '''
        boosts modify attack and defense stats as follows:
        -4: x 4/(4+4)
        -3: x 4/(4+3)
        -2: x 4/(4+2)
        -1: x 4/(4+1)
        +0: x 4/4
        +1: x (4+1)/4
        +2: x (4+2)/4
        +3: x (4+3)/4
        +4: x (4+4)/4
        '''
        self.atk_boost = 0 
        self.def_boost = 0
        self.cooldown = 0
        self.hp = 0
        self.energy = 0
        self.shown = False

    def get_level(self):
        return self.level

    def set_level_cpm(self, l, cpm):
        self.level = l
        self.cpm = cpm
        self.update_stats()

    def set_ivs(self, atk_iv, def_iv, sta_iv):
        self.atk_iv = atk_iv
        self.def_iv = def_iv
        self.sta_iv = sta_iv
        self.update_stats()
    
    def get_cp(self):
        return self.cp

    def get_types(self):
        return self.types
    
    def update_stats(self):
        self.atk_stat = (self.base_atk + self.atk_iv)*self.cpm*(1.2 if self.shadow else 1.0)
        self.def_stat = (self.base_def + self.def_iv)*self.cpm/(1.2 if self.shadow else 1.0)
        self.sta_stat = (self.base_sta + self.sta_iv)*self.cpm
        self.hp = floor(self.sta_stat)
        self.cp = floor(self.atk_stat*pow(self.def_stat, 1/2)*pow(self.sta_stat, 1/2)/10)

    def reset_stats(self):
        self.atk_boost = 0
        self.def_boost = 0
        self.cooldown = 0
        self.hp = floor(self.sta_stat)
        self.energy = 0
    
    def set_team_index(self, ind):
        self.team_index = ind
    
    def get_team_index(self):
        return self.team_index

    def fainted(self):
        return self.hp == 0

    def has_been_shown(self):
        return self.shown

    def get_hp(self):
        return self.hp

    def get_hp_percent(self):
        return self.hp/self.sta_stat

    def get_energy(self):
        return self.energy

    def get_fast_move(self):
        return self.fast_move

    def set_fast_move(self, fast_move):
        self.fast_move = fast_move

    def has_second_charged(self):
        return self.charged_moves['b'] is not None

    def get_all_charged(self):
        return self.charged_moves

    def get_charged_move(self, label):
        return self.charged_moves[label]

    def set_shadow(self, shadow):
        self.shadow = shadow

    def get_ready_charged(self):
        if self.charged_moves['a'] is None:
            raise Exception("Error: Pokemon has no charged moves")

        charged_moves_ready = []
        
        if self.energy >= self.charged_moves['a']['energy_cost']:
            charged_moves_ready.append(self.charged_moves['a'])

        if self.charged_moves['b'] is not None and self.energy >= self.charged_moves['b']['energy_cost']:
            charged_moves_ready.append(self.charged_moves['b'])

        return charged_moves_ready

    def set_charged_moves(self, charged_move_a, charged_move_b = None):
        self.charged_moves['a'] = charged_move_a
        charged_move_a['charged_move_label'] = 'a'
        self.charged_moves['b'] = charged_move_b
        if charged_move_b is not None:
            charged_move_b['charged_move_label'] = 'b'

    def boost_atk(self, stages):
        self.atk_boost = min(max(-4, self.atk_boost + stages), 4)

    def boost_def(self, stages):
        self.def_boost = min(max(-4, self.def_boost + stages), 4)

    def reset_boosts(self):
        self.atk_boost = 0
        self.def_boost = 0

    def get_boosted_atk(self):
        boost_numerator = 4
        boost_denominator = 4
        boost = abs(self.atk_boost)
        if self.atk_boost>=0:
            boost_numerator += boost
        else:
            boost_denominator += boost
        return self.atk_stat * (boost_numerator/boost_denominator)

    def get_boosted_def(self):
        boost_numerator = 4
        boost_denominator = 4
        boost = abs(self.def_boost)
        if self.def_boost>=0:
            boost_numerator += boost
        else:
            boost_denominator += boost
        return self.def_stat * (boost_numerator/boost_denominator)

    def deal_damage(self, damage):
        self.hp = max(0, self.hp - damage)

    def add_energy(self, energy_delta):
        # energy bottoms at 0 and caps at 100
        self.energy = min(max(0, self.energy + energy_delta), 100)

    def start_cooldown(self):
        self.cooldown = self.fast_move['cooldown']

    def decrease_cooldown(self, turns=1):
        self.cooldown = max(0, self.cooldown - turns)
    
    def get_cooldown(self):
        return self.cooldown

    def state_dict(self):
        state = {}
        state['fainted'] = self.fainted()
        state['shown'] = self.has_been_shown()
        state['atk_stat'] = self.get_boosted_atk()
        state['def_stat'] = self.get_boosted_def()
        state['sta_stat'] = self.sta_stat
        state['hp'] = self.get_hp()
        state['energy'] = self.get_energy()
        state['fast_move'] = self.get_fast_move()
        state['charged_move_a'] = self.charged_moves['a']
        if self.has_second_charged():
            state['charged_move_b'] = self.charged_moves['b']
        return state

    def get_name(self):
        return self.name

    def get_id(self):
        return self.pokemon_id

    def __str__(self):
        s = f"{self.name} | CP {self.cp} | IV{self.atk_iv}/{self.def_iv}/{self.sta_iv} | "
        s += f"{self.fast_move['name']}"
        s += f"/{self.charged_moves['a']['name']}"
        s += "(READY)" if self.charged_moves['a'] in self.get_ready_charged() else ""
        if self.charged_moves['b'] is not None:
            s += f"/{self.charged_moves['b']['name']}"
            s += "(READY)" if self.charged_moves['b'] in self.get_ready_charged() else ""
        s += f" | HP Remaining: {self.hp} | Energy: {self.energy}"
        s += f" | Atk Boost: {self.atk_boost} | Def Boost: {self.def_boost}"
        s += f" | Cooldown: {self.cooldown}"
        return s