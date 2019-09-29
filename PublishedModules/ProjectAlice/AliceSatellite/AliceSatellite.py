from typing import Callable

from core.base.SuperManager import SuperManager
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class AliceSatellite(Module):
	_INTENT_TEMPERATURE = Intent('GetTemperature')
	_INTENT_HUMIDITY = Intent('GetHumidity')
	_INTENT_CO2 = Intent('GetCo2Level')
	_INTENT_PRESSURE = Intent('GetPressure')

	_FEEDBACK_SENSORS = 'projectalice/devices/alice/sensorsFeedback'
	_DEVICE_DISCONNECTION = 'projectalice/devices/alice/disconnection'


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._FEEDBACK_SENSORS,
			self._INTENT_TEMPERATURE,
			self._INTENT_HUMIDITY,
			self._INTENT_CO2,
			self._INTENT_PRESSURE,
			self._DEVICE_DISCONNECTION
		]

		self._temperatures = dict()
		self._sensorReadings = dict()

		self.ProtectedIntentManager.protectIntent(self._FEEDBACK_SENSORS)
		self.ProtectedIntentManager.protectIntent(self._DEVICE_DISCONNECTION)

		super().__init__(self._SUPPORTED_INTENTS)


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


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		accepted = False
		if intent == self._INTENT_TEMPERATURE:
			accepted = self.sensorIntent(
				session=session,
				sensorType='temperature',
				placeAnswer='temperaturePlaceSpecific',
				answer='temperature',
				valueConvert=lambda value: value.replace('.0', '')
			)

		elif intent == self._INTENT_HUMIDITY:
			accepted = self.sensorIntent(
				session=session,
				sensorType='humidity',
				placeAnswer='humidityPlaceSpecific',
				answer='humidity',
				valueConvert=lambda value: round(float(value))
			)

		elif intent == self._INTENT_CO2:
			accepted = self.sensorIntent(
				session=session,
				sensorType='gas',
				placeAnswer='c02PlaceSpecific',
				answer='co2'
			)

		elif intent == self._INTENT_PRESSURE:
			accepted = self.sensorIntent(
				session=session,
				sensorType='pressure',
				placeAnswer='pressurePlaceSpecific',
				answer='pressure',
				valueConvert=lambda value: round(float(value))
			)

		elif intent == self._FEEDBACK_SENSORS:
			payload = session.payload
			if 'data' in payload:
				self._sensorReadings[session.siteId] = payload['data']
			accepted = True

		elif intent == self._DEVICE_DISCONNECTION:
			payload = session.payload
			if 'uid' in payload:
				self.DeviceManager.deviceDisconnecting(payload['uid'])
			accepted = True

		return accepted

	# pylint: disable=too-many-arguments
	def sensorIntent(self, session: DialogSession, sensorType: str, placeAnswer: str, answer: str, valueConvert: Callable = None) -> bool:
		place = session.slots.get('Place', session.siteId)
		value = self.getSensorValue(place, sensorType)

		if value == 'undefined':
			return False
		if valueConvert:
			value = valueConvert(value)

		if place != session.siteId:
			self.endDialog(session.sessionId, self.randomTalk(text=placeAnswer, replace=[place, value]))
		else:
			self.endDialog(session.sessionId, self.randomTalk(text=answer, replace=[value]))
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
