from requests import request
from pokemon import Pokemon
import pandas as pd

class GameMaster:
    def __init__(self):
        gm_url = "https://raw.githubusercontent.com/pvpoke/pvpoke/master/src/data/gamemaster.min.json"

        

        self.game_master = request('GET', gm_url).json()

        self.pokemon_master = pd.DataFrame(self.game_master['pokemon'])
        self.move_master = pd.DataFrame(self.game_master['moves']) # fast moves have non-zero 'energyGain', charge moves have non-zero 'energy'
        self.shadow_master = pd.DataFrame(self.game_master['shadowPokemon'], columns=['pokemonId'])

        self.pokemon_ids = self.pokemon_master['speciesId'].to_list()
        self.fast_move_ids = self.move_master[self.move_master['energyGain'] > 0]['moveId']
        self.charged_move_ids = self.move_master[self.move_master['energy'] > 0]['moveId']

        self.type_effectiveness = pd.read_csv('type_effectiveness.csv')
        self.level_cpm = pd.read_csv('level_cpm.csv')

    def get_pokemon_master(self):
        return self.pokemon_master

    # not to be used outside of GameMaster
    def __get_pokemon_entry(self, pokemon_id):
        query = self.pokemon_master[self.pokemon_master['speciesId'] == pokemon_id]
        if len(query) == 0:
            return None
        else:
            return query.iloc[0]

    # not to be used outside of GameMaster
    def __get_move_entry(self, move_id):
        query = self.move_master[self.move_master['moveId'] == move_id]
        if len(query) == 0:
            return None
        else:
            return query.iloc[0]

    # Formatted and flattened pokemon dictionary for team builder 
    def get_pokemon_dict(self, pokemon_id):
        entry = self.__get_pokemon_entry(pokemon_id)
        p = {'pokemon_id': pokemon_id, 'name': entry['speciesName'],
                'base_atk': entry['baseStats']['atk'], 'base_def': entry['baseStats']['def'], 'base_sta': entry['baseStats']['hp'],
                'types': [entry['types'][0], entry['types'][1] if entry['types'][1] != 'none' else None],
                'fast_moves': [self.get_fast_move(fid) for fid in entry['fastMoves'] if self.get_fast_move(fid) is not None],
                'charged_moves': [self.get_charged_move(cid) for cid in entry['chargedMoves'] if self.get_charged_move(cid) is not None],
                'can_shadow': pokemon_id in self.shadow_master}
        print(p['fast_moves'])
        print(p['charged_moves'])
        return p

    def get_all_pokemon_ids(self):
        return self.pokemon_ids.copy()

    # Create a Pokemon object with base stats
    def new_pokemon(self, pokemon_id):
        pd = self.get_pokemon_dict(pokemon_id)
        p = Pokemon(pokemon_id, pd['name'], pd['types'], pd['base_atk'], pd['base_def'], pd['base_sta'])
        if 'shadow' in pd['pokemon_id']:
            p.set_shadow(True)
        return p

    def get_fast_move(self, move_id):
        entry = self.__get_move_entry(move_id)
        if entry is None:
            print(f"Couldn't find move {move_id}")
            return None
        f = {'move_id': move_id, 'name': entry['name'],
                'type': entry['type'], 'power': entry['power'],
                'energy_gain': entry['energyGain'], 'cooldown': entry['cooldown']/ 500}
        return f

    def get_charged_move(self, move_id):
        entry = self.__get_move_entry(move_id)
        if entry is None:
            return None
        c = {'move_id': move_id, 'name': entry['name'],
                'type': entry['type'], 'power': entry['power'],
                'energy_cost': entry['energy'], 'cooldown': entry['cooldown']/ 500}
        if entry['buffTarget'] == 'self':
            if entry['buffs'][0] != 0:
                c['attacker_atk_boost'] = entry['buffs'][0]
                c['attacker_atk_boost_chance'] = float(entry['buffApplyChance'])
            if entry['buffs'][1] != 0:
                c['attacker_def_boost'] = entry['buffs'][1]
                c['attacker_def_boost_chance'] = float(entry['buffApplyChance'])
        if entry['buffTarget'] == 'opponent':
            if entry['buffs'][0] != 0:
                c['defender_atk_boost'] = entry['buffs'][0]
                c['defender_atk_boost_chance'] = float(entry['buffApplyChance'])
            if entry['buffs'][1] != 0:
                c['defender_def_boost'] = entry['buffs'][1]
                c['defender_def_boost_chance'] = float(entry['buffApplyChance'])
            
        return c

    def get_cpm(self, level):
        return self.level_cpm[self.level_cpm['level'] == level].iloc[0]['cpm']

    def get_type_effectiveness(self, attack_type, defender_type):
        return self.type_effectiveness[(self.type_effectiveness['attack_type_id'] == attack_type.upper()) & \
                                        (self.type_effectiveness['defender_type_id'] == defender_type.upper())].iloc[0]['multiplier']