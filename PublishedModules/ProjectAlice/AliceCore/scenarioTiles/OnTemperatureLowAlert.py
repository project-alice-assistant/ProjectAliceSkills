from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class OnTemperatureLowAlert(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.EVENT
		self.name = 'OnTemperatureLowAlert'
		self.description = 'This event triggers if a device reports a temperature lower than your threshold setting'
		self.value = ''


	@staticmethod
	def toCode():
		return f'def onTemperatureLowAlert(self, deviceList: list):'
