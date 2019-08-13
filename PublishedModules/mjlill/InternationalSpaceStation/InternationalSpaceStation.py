# -*- coding: utf-8 -*-

import json
import requests

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class InternationalSpaceStation(Module):
	"""
	Author: mjlill
	Description: Inquire information about the international space station
	"""

	_INTENT_ASTRONAUTS = Intent('Astronauts')
	_INTENT_ISS_POSITION = Intent('IssPosition')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_ASTRONAUTS,
			self._INTENT_ISS_POSITION
		]

		super().__init__(self._SUPPORTED_INTENTS)

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId

		try:
			if intent == self._INTENT_ASTRONAUTS:
				text = self.getAstronauts()
			elif intent == self._INTENT_ISS_POSITION:
				text = self.getIssPosition()

			managers.MqttServer.endTalk(sessionId, text=text)
		except Exception as e:
			self._logger.error(e)
			managers.MqttServer.endTalk(sessionId,
										text=managers.TalkManager.randomTalk(module=self.name, talk='noServer'))

		return True

	def queryApi(self, url: str) -> dict:
		return requests.get(url=url).json

	def getIssPosition(self) -> str:
		data = self.queryApi('http://api.open-notify.org/iss-now.json')
		location = data['iss_position']
		return managers.TalkManager.randomTalk(module=self.name, talk='issPosition').format(
			float(location['latitude']),
			float(location['longitude'])
		)

	def getAstronauts(self) -> str:
		data = self.queryApi('http://api.open-notify.org/astros.json')
	
		amount = data['number']
		if not amount:
			return managers.TalkManager.getrandomTalk('noAstronauts')
		if amount == 1:
			return managers.TalkManager.randomTalk(module=self.name, talk='oneAstronaut').format(
				data['people'][0]['name']
			)

		return managers.TalkManager.randomTalk(module=self.name, talk='multipleAstronauts').format(
				', '.join(str(x['name']) for x in data['people'][:-1]),
				data['people'][-1]['name'],
				amount
			)
		