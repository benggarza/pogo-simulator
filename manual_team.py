from team_builder import TeamBuilder
from game_master import GameMaster
class ManualTeam(TeamBuilder):
    def __init__(self, game_master, team_ids):
        self.gm = game_master
        self.team_ids = team_ids

    def choose_team(self, cup):
        cp_limit = cup['cp']

        # Get new pokemon objects for each team member
        team = [self.gm.new_pokemon(team_id) for team_id in self.team_ids]
        team_dicts = [self.gm.get_pokemon_dict(team_id) for team_id in self.team_ids]

        # Choose moves, Set IVs, and Calculate highest CP
        for p, pd in zip(team, team_dicts):
            p.set_ivs(0, 15 ,15)
            p.set_fast_move(pd['fast_moves'][0])
            p.set_charged_moves(pd['charged_moves'][0], None)
            cp = p.get_cp()
            level = p.get_level()
            while cp <= cp_limit and level <= 50:
                cpm = self.gm.get_cpm(level)
                p.set_level_cpm(level, cpm)
                cp = p.get_cp()
                level += 0.5
            # Drop by one level too keep cp under limit
            p.set_level_cpm(level-1.0, self.gm.get_cpm(level-1.0))

        print("TEAM")
        for p in team:
            print(p)
        return team

    def __str__(self):
        return "manual"