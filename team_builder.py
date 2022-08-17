### Pseudo-Interface for Team Builders

class TeamBuilder:
    def __init__(self, game_master):
        self.gm = game_master

    def choose_team(self, cup):
        raise NotImplementedError("Error: choose_team() method not implemented in this team builder")
    
    '''def choose_fast_move(self, pokemon_dict, fast_moves):
        raise NotImplementedError("Error: choose_fast_move() method not implemented in this team builder")

    def choose_charged_moves(self, pokemon_dict, charged_moves):
        raise NotImplementedError("Error: choose_charged_move() method not implemented in this team builder")'''

    def set_cp(self, p, cup):
        cp_limit = cup['cp']
        cp = p.get_cp()
        level = p.get_level()
        while cp <= cp_limit and level <= 50:
            cpm = self.gm.get_cpm(level)
            p.set_level_cpm(level, cpm)
            cp = p.get_cp()
            level += 0.5
        # Drop by one level too keep cp under limit
        p.set_level_cpm(level-1.0, self.gm.get_cpm(level-1.0))