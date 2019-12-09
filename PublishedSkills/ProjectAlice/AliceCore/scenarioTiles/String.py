from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class String(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.STRING
		self.name = 'String'
		self.description = 'A string is a variable type that stores chains of characters, by default empty'
		self.value = ''


	def toCode(self) -> str:
		return self.value
