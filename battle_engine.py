from battle import Battle
class BattleEngine:
    def __init__(self, gm):
        self.gm = gm

    def new_battle(self, player_a, player_b, cup):
        b = Battle(self.gm)
        if player_a.team_empty() or player_b.team_empty():
            raise Exception("Error: player team not set")

        a_ids = []
        for p in player_a.get_team():
            if p.get_cp() > cup['cp']:
                raise Exception(f"Error: Player A team member over {cup['cp']} cp limit for {cup['name']} league")
            if p.get_id() in a_ids:
                raise Exception(f"Error: Duplicate pokemon in Player A team ({p.get_id()})")
            a_ids.append(p.get_id())

        b_ids = []
        for p in player_b.get_team():
            if p.get_cp() > cup['cp']:
                raise Exception(f"Error: Player B team member over {cup['cp']} cp limit for {cup['name']} league")
            if p.get_id() in b_ids:
                raise Exception(f"Error: Duplicate pokemon in Player B team({p.get_id()})")
            b_ids.append(p.get_id())

        b.add_players(player_a, player_b)

        return b