from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class Boolean(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.VARIABLE
		self.name = 'Boolean'
		self.description = 'A boolean is a variable type that stores either True or False, by default False'
		self.value = False


	def toCode(self) -> bool:
		return self.value


	def interfaceName(self) -> str:
		return 'true' if self.value else 'false'
