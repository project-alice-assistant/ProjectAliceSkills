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
	_INTENT_ZIGBEE_MSG = 'zigbee2mqtt/#'

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			(self._INTENT_ZIGBEE_STATE, self.bridgeStateReport),
			(self._INTENT_ZIGBEE_MSG, self.handleMessage)
		]
		self._online = False

		super().__init__(self._SUPPORTED_INTENTS)


	def bridgeStateReport(self, session: DialogSession, **_kwargs):
		if 'online' in session.payload:
			self._online = True
			self.logInfo('Now online')
		else:
			self._online = False
			self.logInfo('Now offline')


	def handleMessage(self, session: DialogSession, **_kwargs):
		print(session.payload)


	def onStart(self) -> list:
		super().onStart()
		subprocess.run(['sudo', 'systemctl', 'start', 'zigbee2mqtt'])
		self.MqttManager.publish(topic='zigbee2mqtt/bridge/config/permit_join', payload='false')
		return self.supportedIntents


	def onStop(self):
		super().onStop()
		subprocess.run(['sudo', 'systemctl', 'stop', 'zigbee2mqtt'])
