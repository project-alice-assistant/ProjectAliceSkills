from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.model.TelemetryType import TelemetryType


class Telemetry(Module):
	"""
	Author: Psychokiller1888
	Description: Access your stored telemetry data
	"""

	_INTENT_GET_TELEMETRY_DATA = Intent('GetTelemetryData')
	_INTENT_ANSWER_TELEMETRY_TYPE = Intent('AnswerTelemetryType')

	def __init__(self):
		self._INTENTS	= [
			(self._INTENT_GET_TELEMETRY_DATA, self.telemetryIntent),
			(self._INTENT_ANSWER_TELEMETRY_TYPE, self.telemetryIntent)
		]

		super().__init__(self._INTENTS)

		self._telemetryUnits = {
			'airQuality': '%',
			'co2': 'ppm',
			'gas': 'ppm',
			'gust_angle': '°',
			'gust_strength': 'km/h',
			'humidity': '%',
			'light': 'lux',
			'pressure': 'mb',
			'rain': 'mm',
			'temperature': '°C',
			'wind_angle': '°',
			'wind_strength': 'km/h'
		}


	def telemetryIntent(self, session: DialogSession, **_kwargs):
		slots = session.slots
		siteId = session.siteId

		if 'Room' in slots:
			siteId = session.slotValue('Room')

		if 'TelemetryType' not in slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('noType'),
				intentFilter=[self._INTENT_ANSWER_TELEMETRY_TYPE],
				slot='TelemetryType'
			)

		telemetryType = session.slotValue('TelemetryType')

		data = self.TelemetryManager.getData(siteId=siteId, ttype=TelemetryType(telemetryType))

		if data[0]:
			answer = data['value'] + self._telemetryUnits.get(telemetryType, '')
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('answerInstant').format(answer))
		else:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('noData'))
