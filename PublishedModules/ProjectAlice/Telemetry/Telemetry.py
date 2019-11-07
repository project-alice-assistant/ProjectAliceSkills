from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.model.TelemetryType import TelemetryType
from core.util.Decorators import IntentHandler


class Telemetry(Module):
	"""
	Author: Psychokiller1888
	Description: Access your stored telemetry data
	"""

	def __init__(self):
		super().__init__()

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

	@IntentHandler('GetTelemetryData')
	@IntentHandler('AnswerTelemetryType')
	def telemetryIntent(self, session: DialogSession, **_kwargs):
		siteId = session.slotValue('Room') or session.siteId
		telemetryType = session.slotValue('TelemetryType')

		if not telemetryType:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('noType'),
				intentFilter=[Intent('AnswerTelemetryType')],
				slot='TelemetryType'
			)

		data = self.TelemetryManager.getData(siteId=siteId, ttype=TelemetryType(telemetryType))

		if data and 'value' in data:
			answer = f"{data['value']} {self._telemetryUnits.get(telemetryType, '')}"
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('answerInstant').format(answer))
		else:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('noData'))
