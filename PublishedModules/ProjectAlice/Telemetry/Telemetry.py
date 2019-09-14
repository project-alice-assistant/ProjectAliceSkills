from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Telemetry(Module):
	"""
	Author: Psychokiller1888
	Description: Access your stored telemetry data
	"""

	_INTENT_GET_TELEMETRY_DATA = Intent('GetTelemetryData')
	_INTENT_ANSWER_TELEMETRY_TYPE = Intent('AnswerTelemetryType')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_GET_TELEMETRY_DATA,
			self._INTENT_ANSWER_TELEMETRY_TYPE
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		slots = session.slots

		if intent == self._INTENT_GET_TELEMETRY_DATA or intent == self._INTENT_ANSWER_TELEMETRY_TYPE:
			if 'siteId' in slots:
				siteId = session.slotValue('Room')

			if 'TelemetryType' not in slots:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('noType'),
					intentFilter=[self._INTENT_ANSWER_TELEMETRY_TYPE],
					slot='TelemetryType'
				)

			telemetryType = session.slotValue('TelemetryType')

			data = self.TelemetryManager.getData(siteId=siteId, ttype=telemetryType)
			print(data)

		return True