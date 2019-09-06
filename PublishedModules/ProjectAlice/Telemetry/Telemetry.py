import json

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Telemetry(Module):
	"""
	Author: Psychokiller1888
	Description: Access your stored telemetry data
	"""

	_INTENT_GET_TELEMETRY_DATA = Intent('GetTelemetryData')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_GET_TELEMETRY_DATA
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		siteId = session.siteId
		slots = session.slots

		if intent == self._INTENT_GET_TELEMETRY_DATA:
			if 'siteId' in slots:
				siteId = session.slotValue('Room')

			if 'TelemetryType' in slots:
				ttype = session.slotValue('TelemetryType')

			data = managers.TelemetryManager.getData(siteId=siteId, ttype=ttype)
			print(data)

		return True