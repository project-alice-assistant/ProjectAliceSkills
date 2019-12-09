from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class Float(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.FLOAT
		self.name = 'Float'
		self.description = 'A float is a variable type that stores numbers with decimals, by default 0'
		self.value = 0


	def toCode(self) -> float:
		return self.value
