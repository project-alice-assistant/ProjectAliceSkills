from core.base.SuperManager import SuperManager
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class AliceSatellite(Module):
	_FEEDBACK_SENSORS = 'projectalice/devices/alice/sensorsFeedback'
	_DEVICE_DISCONNECTION = 'projectalice/devices/alice/disconnection'


	def __init__(self):
		self._INTENTS = {
			self._FEEDBACK_SENSORS: self.feedbackSensorIntent,
			self._DEVICE_DISCONNECTION: self.deviceDisconnectIntent
		}

		self._sensorReadings = dict()

		self.ProtectedIntentManager.protectIntent(self._FEEDBACK_SENSORS)
		self.ProtectedIntentManager.protectIntent(self._DEVICE_DISCONNECTION)

		super().__init__(self._INTENTS)


	def onBooted(self):
		confManager = SuperManager.getInstance().configManager
		if confManager.configAliceExists('onReboot') and confManager.getAliceConfigByName('onReboot') == 'greetAndRebootModules':
			self.restartDevice()


	def onSleep(self):
		self.broadcast('projectalice/devices/sleep')


	def onWakeup(self):
		self.broadcast('projectalice/devices/wakeup')


	def onGoingBed(self):
		self.broadcast('projectalice/devices/goingBed')


	def onFullMinute(self):
		self.getSensorReadings()

	
	def feedbackSensorIntent(self, intent: str, session: DialogSession) -> bool:
		payload = session.payload
		if 'data' in payload:
			self._sensorReadings[session.siteId] = payload['data']
		return True


	def deviceDisconnectIntent(self, intent: str, session: DialogSession) -> bool:
		payload = session.payload
		if 'uid' in payload:
			self.DeviceManager.deviceDisconnecting(payload['uid'])
		return True


	def getSensorReadings(self):
		self.broadcast('projectalice/devices/alice/getSensors')


	def temperatureAt(self, siteId: str) -> str:
		return self.getSensorValue(siteId, 'temperature')


	def getSensorValue(self, siteId: str, value: str) -> str:
		return self._sensorReadings.get(siteId, dict()).get(value, 'undefined')


	def restartDevice(self):
		devices = self.DeviceManager.getDevicesByType(deviceType=self.name, connectedOnly=True, onlyOne=False)
		if not devices:
			return

		for device in devices:
			self.publish(topic='projectalice/devices/restart', payload={'uid': device.uid})
