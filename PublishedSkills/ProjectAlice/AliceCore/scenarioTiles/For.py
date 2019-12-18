from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class For(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.LOOP_BLOCK
		self.name = 'For'
		self.description = 'For blocks will run their child blocks on all elements of an array'
		self.value = ''


	@staticmethod
	def toCode() -> str:
		return 'for'
