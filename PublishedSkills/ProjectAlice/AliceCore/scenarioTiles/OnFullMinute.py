from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class OnFullMinute(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.EVENT
		self.name = 'On full minute'
		self.description = 'This event triggers every full minute'


	@staticmethod
	def toCode():
		return f'def onFullMinute(self):'
