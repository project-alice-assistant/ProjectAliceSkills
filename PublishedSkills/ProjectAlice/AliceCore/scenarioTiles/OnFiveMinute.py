from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class OnFiveMinute(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.EVENT
		self.name = 'On five minute'
		self.description = 'This event triggers every 5 minutes'


	@staticmethod
	def toCode():
		return f'def onFiveMinute(self):'
