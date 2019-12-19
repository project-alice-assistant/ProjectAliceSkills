from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler


class HomeAssistant(AliceSkill):
	"""
	Author: maxbachmann
	Description: bridge events between alice and HomeAssistant
	"""

	def onEvent(self, event: str, **kwargs):
		self.MqttManager.publish(topic=f'projectalice/events/{event}', payload=kwargs)


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


