from random import Random
from model_master import ModelMaster
from random_model import RandomModel
from manual_team import ManualTeam
from random_team import RandomTeam
from game_master import GameMaster
gm = GameMaster()
a_team_ids = ['machamp','spewpa','skarmory']
b_team_ids = ['dialga', 'swampert', 'scrafty']
random_model = RandomModel()
#a_manual_builder = ManualTeam(gm, a_team_ids)
a_manual_builder = RandomTeam(gm)
b_manual_builder = RandomTeam(gm)

mm = ModelMaster(gm, a_manual_builder, random_model, b_manual_builder, random_model, 1000, verbose=True)
mm.run()