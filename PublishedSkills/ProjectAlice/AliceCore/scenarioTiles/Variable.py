from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class Variable(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.VARIABLE
		self.name = 'Variable'
		self.description = 'A variable acts like a named container in which you can then store a value'
		self.value = ''

	def toCode(self) -> str:
		return self.interfaceName()


	def interfaceName(self) -> str:
		if not self.value:
			self.logWarning('Tile of type variable has no value defined')
		else:
			return self.value
