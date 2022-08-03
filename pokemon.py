class Pokemon:
    def __init__():
        team_index = -1
        player=None

        types = []

        name = ""
        cp = 0
        atk_iv = 0
        def_iv = 0
        sta_iv = 0
        atk_stat = 0
        def_stat = 0
        sta_stat = 0 # same as to full HP

        fast_move = None
        charged_moves = {'a': None, 'b': None}

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
        atk_boost = 0 
        def_boost = 0
        cooldown = 0
        hp = 0
        energy = 0
        shown = False

    def reset_stats(self):
        self.atk_boost = 0
        self.def_boost = 0
        self.cooldown = 0
        self.hp = self.sta_stat
        self.energy = 0

    def fainted(self):
        return self.hp > 0

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

    def has_second_charged(self):
        return self.charged_moves['b'] is not None

    def get_all_charged(self):
        return self.charged_moves

    def get_ready_charged(self):
        if self.charged_moves['a'] is None:
            raise Exception("Error: Pokemon has no charged moves")

        charged_moves_ready = []
        
        if self.energy >= self.charged_moves['a'].energy_cost:
            charged_moves_ready.append(self.charged_moves['a'])

        if self.charged_moves['b'] is not None and self.energy >= self.charged_moves['b'].energy_cost:
            charged_moves_ready.append(self.charged_moves['b'])

        return charged_moves_ready

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

    def __str__(self):
        s = "" + self.name + " | CP" + self.cp + \
                "; IV " + self.atk_iv + "/" + self.def_iv + "/" + self.sta_iv + \
                "\n" + self.fast_move['name'] + "/" + \
                self.charged_moves['a']['name'] + ("(READY)" if self.charged_moves['a'] in self.get_ready_charged() else "") + \
                ("/"+self.charged_moves['b']['name'] + ("(READY)" if self.charged_moves['b'] in self.get_ready_charged() else "")) if self.has_second_charged() else ""

        s += "\nHP Remaining: " + self.hp + "; Energy: " + self.energy
        s += "\nAtk Boost: " + self.atk_boost + "; Def Boost: " + self.def_boost
        s += "\nCooldown: " + self.cooldown
        return s