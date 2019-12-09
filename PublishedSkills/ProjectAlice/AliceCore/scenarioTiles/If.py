from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class If(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.CONDITION_BLOCK
		self.name = 'If'
		self.description = 'If conditions are used to check if a parameter is equal to a certain value'
		self.value = ''


	@staticmethod
	def toCode() -> str:
		return 'if'
