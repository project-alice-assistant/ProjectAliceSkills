# -*- coding: utf-8 -*-

import alice.base.Managers as managers
from alice.base.model.Intent import Intent
from alice.base.model import Module
from alice.dialog.model.DialogSession import DialogSession
import requests


class IcanhazdadjokeDotCom(Module):

	NAME 				= 'IcanhazdadjokeDotCom'
	_INTENT_TELL_A_JOKE = Intent('hermes/intent/{owner}:tellAJoke')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_TELL_A_JOKE
		]

		super(IcanhazdadjokeDotCom, self).__init__(self.NAME, self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_TELL_A_JOKE:
			url = 'https://icanhazdadjoke.com/'

			headers = {
				'Accept': 'text/plain',
				'User-Agent': 'Project Alice',
				'From': 'projectalice@gmail.com'
			}

			response = requests.get(url, headers=headers)
			if response is not None:
				managers.MqttServer.endTalk(session.sessionId, text=response.text)
			else:
				managers.MqttServer.endTalk(session.sessionId, managers.TalkManager.getRandomTalk(self.name, 'noJoke'))

		return True
