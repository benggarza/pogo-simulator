from battle import Battle
class BattleEngine:
    def __init__(self, gm):
        self.gm = gm

    def new_battle(self, player_a, player_b, cup):
        b = Battle(self.gm)
        if player_a.team_empty() or player_b.team_empty():
            raise Exception("Error: player team not set")

        ### TODO Check that player teams are valid for the given cup
        for p in player_a.get_team():
            if p.get_cp() > cup['cp']:
                raise Exception(f"Error: Player A team member over {cup['cp']} cp limit for {cup['name']} league")

        for p in player_b.get_team():
            if p.get_cp() > cup['cp']:
                raise Exception(f"Error: Player B team member over {cup['cp']} cp limit for {cup['name']} league")

        b.add_players(player_a, player_b)

        return b