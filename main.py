from random import Random
from model_master import ModelMaster
from random_model import RandomModel
from manual_team import ManualTeam
from game_master import GameMaster
gm = GameMaster()
team_ids = ['machamp','mewtwo','skarmory']
random_model = RandomModel()
manual_builder = ManualTeam(gm, team_ids)

mm = ModelMaster(gm, manual_builder, random_model, manual_builder, random_model, 1)
mm.run()