from team_builder import TeamBuilder
from game_master import GameMaster
from random import randint
class RandomTeam(TeamBuilder):
    def choose_team(self, cup):
        pokemon_ids = self.gm.get_all_pokemon_ids()
        team_ids = []
        for i in range(3):
            pid = pokemon_ids[randint(0,len(pokemon_ids)-1)]
            team_ids.append(pid)
            pokemon_ids.remove(pid)

        print(f"Selected team {team_ids}")

        # Get new pokemon objects for each team member
        team = [self.gm.new_pokemon(team_id) for team_id in team_ids]
        team_dicts = [self.gm.get_pokemon_dict(team_id) for team_id in team_ids]

        # Choose moves, Set IVs, and Calculate highest CP
        for p, pd in zip(team, team_dicts):
            ivs = [randint(0,15), randint(0,15), randint(0,15)]
            print(f"For {p.get_name()}, selected ivs {ivs}")
            p.set_ivs(*ivs)
            fast_move = pd['fast_moves'][randint(0, len(pd['fast_moves'])-1)]
            print(f"For {p.get_name()}, selected fast move {fast_move['name']}")
            p.set_fast_move(fast_move)
            charged_move_a = pd['charged_moves'][randint(0, len(pd['charged_moves'])-1)]
            print(f"For {p.get_name()}, selected first charged move {charged_move_a['name']}")
            remaining_charged_moves = [c for c in pd['charged_moves'] if c['move_id'] != charged_move_a['move_id']]
            charged_move_b = None
            if len(remaining_charged_moves) > 0:
                charged_move_b = remaining_charged_moves[randint(0, len(remaining_charged_moves)-1)]
                print(f"For {p.get_name()}, selected second charged move {charged_move_b['name']}")
            p.set_charged_moves(charged_move_a, charged_move_b)
            self.set_cp(p, cup)

        print("TEAM")
        for p in team:
            print(p)
        return team

    def __str__(self):
        return "random"