import subprocess

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Zigbee2Mqtt(Module):
	"""
	Author: Psychokiller1888
	Description: Have your zigbee devices communicate with alice directly over mqtt
	"""

	_INTENT_ZIGBEE_STATE = Intent('zigbee2mqtt/bridge/state', isProtected=True, userIntent=False)
	_INTENT_ZIGBEE_MSG = 'zigbee2mqtt/*'

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			(self._INTENT_ZIGBEE_STATE, self.bridgeStateReport)
		]

		self._active = True

		super().__init__(self._SUPPORTED_INTENTS)


	def bridgeStateReport(self, session: DialogSession, **_kwargs):
		if 'online' in session.payload:
			self._active = True
		else:
			self._active = False


	def onStart(self) -> list:
		super().onStart()
		subprocess.run(['sudo', 'systemctl', 'start', 'zigbee2mqtt'])
		return self._SUPPORTED_INTENTS


	def onStop(self):
		super().onStop()
		subprocess.run(['sudo', 'systemctl', 'stop', 'zigbee2mqtt'])
