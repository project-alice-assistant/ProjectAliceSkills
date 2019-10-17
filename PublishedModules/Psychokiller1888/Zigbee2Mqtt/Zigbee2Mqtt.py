import getpass
import subprocess
from pathlib import Path

from core.base.model.Module import Module
from core.commons import commons
from core.dialog.model.DialogSession import DialogSession


class Zigbee2Mqtt(Module):
	"""
	Author: Psychokiller1888
	Description: Have your zigbee devices communicate with alice directly over mqtt
	"""

	_INTENT_ZIGBEE_STATE = 'zigbee2mqtt/bridge/state'
	_INTENT_ZIGBEE_MSG = ''

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			(self._INTENT_ZIGBEE_STATE, self.bridgeStateReport)
		]

		self._active = False

		super().__init__(self._SUPPORTED_INTENTS)


	def bridgeStateReport(self, session: DialogSession, **_kwargs):
		print(session.payload)
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
