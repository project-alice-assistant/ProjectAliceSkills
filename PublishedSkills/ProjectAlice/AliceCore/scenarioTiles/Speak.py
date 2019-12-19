from core.scenario.model.ScenarioTile import ScenarioTile
from core.scenario.model.ScenarioTileType import ScenarioTileType


class Speak(ScenarioTile):

	def __init__(self):
		super().__init__()

		self.tileType = ScenarioTileType.ACTION
		self.name = 'Speak'
		self.description = 'The speak action makes Alice speak aloud the given text on the given device'
		self.value = list()


	def toCode(self):
		if not self.value:
			self.logWarning('Speak action tile has no text to be spoken')
			return

		return f'self.MqttManager.say(text=self.value[0], siteId=self.value[1], canBeEnqueued=True)'
