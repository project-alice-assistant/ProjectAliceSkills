from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class While(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.LOOP_BLOCK
		self.name = 'While'
		self.description = 'While blocks will run their child blocks until a condition you define is met'
		self.value = ''


	@staticmethod
	def toCode() -> str:
		return 'while'
