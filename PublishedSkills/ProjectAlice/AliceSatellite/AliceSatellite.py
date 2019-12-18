from core.base.SuperManager import SuperManager
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import MqttHandler


class AliceSatellite(AliceSkill):

	def __init__(self):
		self._sensorReadings = dict()
		super().__init__()


	def onBooted(self):
		confManager = SuperManager.getInstance().configManager
		if confManager.configAliceExists('onReboot') and confManager.getAliceConfigByName('onReboot') == 'greetAndRebootSkillss':
			self.restartDevice()


	def onSleep(self):
		self.publish('projectalice/devices/sleep')


	def onWakeup(self):
		self.publish('projectalice/devices/wakeup')


	def onGoingBed(self):
		self.publish('projectalice/devices/goingBed')


	def onFullMinute(self):
		self.getSensorReadings()


	@MqttHandler('projectalice/devices/alice/sensorsFeedback')
	def feedbackSensorIntent(self, session: DialogSession):
		data = session.payload.get('data')
		if data:
			self._sensorReadings[session.siteId] = data


	@MqttHandler('projectalice/devices/alice/disconnection')
	def deviceDisconnectIntent(self, session: DialogSession):
		uid = session.payload.get('uid')
		if uid:
			self.DeviceManager.deviceDisconnecting(uid)


	def getSensorReadings(self):
		self.publish('projectalice/devices/alice/getSensors')


	def temperatureAt(self, siteId: str) -> str:
		return self.getSensorValue(siteId, 'temperature')


	def getSensorValue(self, siteId: str, value: str) -> str:
		return self._sensorReadings.get(siteId, dict()).get(value, 'undefined')


	def restartDevice(self):
		devices = self.DeviceManager.getDevicesByType(deviceType=self.name, connectedOnly=True, onlyOne=False)
		for device in devices:
			self.publish(topic='projectalice/devices/restart', payload={'uid': device.uid})
