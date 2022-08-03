from battle import Battle
class BattleEngine:
    def __init__():
        pass

    def create_battle(self, player_a, player_b, cup):
        b = Battle()
        if player_a.team_empty() or player_b.team_empty():
            raise Exception("Error: player team not set")

        ### TODO Check that player teams are valid for the given cup

        b.add_players(player_a, player_b)

        return b