from paho.mqtt import client as MQTTClient

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler


class MqttBridge(AliceSkill):
	"""
	Author: maxbachmann
	Description: bridge events between alice and mqtt
	"""

	def onEvent(self, event: str, **kwargs):
		self.MqttManager.mqttClient.unsubscribe('projectalice/events/+')
		self.MqttManager.publish(topic=f'projectalice/events/{event}', payload=kwargs)
		self.MqttManager.mqttClient.subscribe('projectalice/events/+')


	@MqttHandler('projectalice/events/+')
	def incomingEventHandler(self, session: DialogSession):
		eventName = session.intentName.replace('projectalice/events/', '')
		payload = self.Commons.payload(session.message)

		try:
			self.SkillManager.skillBroadcast(method=eventName, **payload)
			argumentLog = ', '.join([f'{name}={value}' for name, value in payload.items()])
			self.logInfo(f'broadcasting {eventName} with the arguments: {argumentLog}')
		except TypeError:
			self.logError(f'broadcasting {eventName} failed: The payload {payload} is not supported')


	@MqttHandler('projectalice/dialog/say')
	def sayDialogHandler(self, session: DialogSession):
		payload = self.Commons.payload(session.message)
		
		try:
			self.say(**payload)
		except TypeError:
			self.logError(f'incoming message say was ignored: The payload {payload} is not supported')


