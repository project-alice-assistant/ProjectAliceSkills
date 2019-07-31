# -*- coding: utf-8 -*-

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession

try:
	from modules.Ifttt.Ifttt import IftttException
except:
	pass

class FindMyPhone(Module):
	"""
	Author: Psychokiller1888
	Description: Using ifttt one can ask alice to find his phone. sets the ring tone at max volume and initiates a call on it.
	"""

	_INTENT_FIND_PHONE = Intent('FindPhone')
	_INTENT_ANSWER_NAME = Intent('AnswerName', isProtected=True)

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_FIND_PHONE,
			self._INTENT_ANSWER_NAME
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		slots = session.slots

		if session.user == 'unknown' and 'who' not in slots.keys():
			managers.MqttServer.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('whosPhone'),
				intentFilter=[self._INTENT_ANSWER_NAME],
				previousIntent=self._INTENT_FIND_PHONE
			)
		else:
			if 'who' in slots.keys():
				who = slots['who']
			elif 'name' in slots.keys():
				who = slots['name']
			else:
				who = session.user

				answer = managers.ModuleManager.getModuleInstance('Ifttt').sendRequest(endPoint='locatePhone', user=who)
				if answer == IftttException.NOT_CONNECTED:
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('notConnected'))
				elif answer == IftttException.ERROR or answer == IftttException.BAD_REQUEST:
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('error'))
				elif answer == IftttException.NO_USER:
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('unknown').format(who))
				else:
					managers.MqttServer.endTalk(sessionId=sessionId, text=self.randomTalk('aknowledge'))

		return True
