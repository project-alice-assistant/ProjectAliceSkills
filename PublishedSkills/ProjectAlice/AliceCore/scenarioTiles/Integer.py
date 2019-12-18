from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class Integer(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.INTEGER
		self.name = 'Integer'
		self.description = 'An integer is a variable type that stores numbers without any decimal, by default 0'
		self.value = 0


	def toCode(self) -> int:
		return self.value
