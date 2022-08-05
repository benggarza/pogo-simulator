from random import Random
from model_master import ModelMaster
from random_model import RandomModel
from manual_team import ManualTeam
from game_master import GameMaster
gm = GameMaster()
a_team_ids = ['machamp','venusaur','skarmory']
b_team_ids = ['dialga', 'swampert', 'scrafty']
random_model = RandomModel()
a_manual_builder = ManualTeam(gm, a_team_ids)
b_manual_builder = ManualTeam(gm, b_team_ids)

mm = ModelMaster(gm, a_manual_builder, random_model, b_manual_builder, random_model, 1)
mm.run()