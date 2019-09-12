from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Zigbee2Mqtt(Module):
	"""
	Author: Psychokiller1888
	Description: Have you zigbee devices communicate with alice directly over mqtt
	"""

	def __init__(self):
		self._SUPPORTED_INTENTS	= []
		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False