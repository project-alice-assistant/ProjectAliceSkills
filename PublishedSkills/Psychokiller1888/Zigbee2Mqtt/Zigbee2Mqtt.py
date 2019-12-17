import subprocess

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler


class Zigbee2Mqtt(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Have your zigbee devices communicate with alice directly over mqtt
	"""

	def __init__(self):
		self._online = False
		super().__init__()


	@MqttHandler('zigbee2mqtt/bridge/state')
	def bridgeStateReport(self, session: DialogSession):
		if 'online' in session.payload:
			self._online = True
			self.logInfo('Now online')
		else:
			self._online = False
			self.logInfo('Now offline')


	@MqttHandler('zigbee2mqtt/#')
	def handleMessage(self, session: DialogSession):
		print(session.payload)


	def onStart(self) -> list:
		super().onStart()
		subprocess.run(['sudo', 'systemctl', 'start', 'zigbee2mqtt'])
		self.MqttManager.publish(topic='zigbee2mqtt/bridge/config/permit_join', payload='false')
		return self.supportedIntents


	def onStop(self):
		super().onStop()
		subprocess.run(['sudo', 'systemctl', 'stop', 'zigbee2mqtt'])
