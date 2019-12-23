from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class OnQuarterHour(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.EVENT
		self.name = 'On quarter hour'
		self.description = 'This event triggers every 15 minutes'


	@staticmethod
	def toCode():
		return f'def onQuarterHour(self):'
