from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class Array(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.ARRAY
		self.name = 'Array'
		self.description = 'An array is a variable type that stores one or more values of different types. The values cannot be duplicated in an array'
		self.value = list()


	def toCode(self) -> str:
		return f'[{", ".join(self.value)}]'
