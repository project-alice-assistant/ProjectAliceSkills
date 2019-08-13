# -*- coding: utf-8 -*-

import json
import requests

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Astronauts(Module):
	"""
	Author: mjlill
	Description: Inquire a list of names of current astronauts
	"""

	_INTENT_ASTRONAUTS = Intent('Astronauts')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_ASTRONAUTS
		]

		super().__init__(self._SUPPORTED_INTENTS)

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId

		
		if intent == self._INTENT_ASTRONAUTS:
			try:
				url = 'http://api.open-notify.org/astros.json'
	
				req = requests.get(url=url)
				data = req.json
	
				amount = data['number']
				if not amount:
					text = managers.TalkManager.getrandomTalk('noAstronauts')
				elif amount == 1:
					text = managers.TalkManager.randomTalk(module=self.name, talk='oneAstronaut').format(
						data['people'][0]['name']
					)
				else:
					text = managers.TalkManager.randomTalk(module=self.name, talk='multipleAstronauts').format(
						', '.join(str(x['name']) for x in data['people'][:-1]),
						data['people'][-1]['name'],
						amount
					)
				managers.MqttServer.endTalk(sessionId, text=text)
			except Exception as e:
				self._logger.error(e)
				managers.MqttServer.endTalk(sessionId,
											text=managers.TalkManager.randomTalk(module=self.name, talk='noServer'))

		return True