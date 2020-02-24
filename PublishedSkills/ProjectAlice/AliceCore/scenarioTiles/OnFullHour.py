from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class OnFullHour(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.EVENT
		self.name = 'On full hour'
		self.description = 'This event triggers every hour'


	@staticmethod
	def toCode():
		return f'def onFullHour(self):'
