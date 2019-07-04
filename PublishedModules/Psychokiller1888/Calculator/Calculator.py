# -*- coding: utf-8 -*-

import json

import math

import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Calculator(Module):
	"""
	Author: Psychokiller1888
	Description: Do some calculation with alice
	"""

	_INTENT_MATHS = Intent(Intent('Maths'))

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_MATHS
		]
		self._lastNumber = None
		super(Calculator, self).__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		slots = session.slotsAsObjects
		sessionId = session.sessionId

		if intent == self._INTENT_MATHS:
			if ('Left' not in slots and 'Right' not in slots) or 'Function' not in slots:
				managers.MqttServer.continueDialog(sessionId=sessionId, text=managers.TalkManager.randomTalk(self.name, 'notUnderstood'))
				return True

			func = slots['Function'][0].value['value']

			if 'Left' in slots and 'Right' in slots:
				result = self.calculate(float(slots['Left'][0].value['value']), float(slots['Right'][0].value['value']), func)

			elif 'Right' in slots and 'Left' not in slots:
				if not self._lastNumber:
					managers.MqttServer.endTalk(sessionId=sessionId, text=managers.TalkManager.randomTalk(self.name, 'noPreviousOperation'), client=siteId)
					return True

				result = self.calculate(self._lastNumber, float(slots['Right'][0].value['value']), func)

			else:
				managers.MqttServer.continueDialog(sessionId=sessionId, text=managers.TalkManager.randomTalk(self.name, 'notUnderstood'), client=siteId)
				return True

			if str(result).endswith('.0'):
				answer = str(result).replace('.0', '')
			else:
				answer = str(result)

			managers.MqttServer.endTalk(sessionId=sessionId, text=answer, client=siteId)

		return True


	def calculate(self, left: float, right: float, func: str) -> float:
		if func == '+':
			result = left + right
		elif func == '-':
			result = left - right
		elif func == '/':
			result = left / right
		elif func == '*':
			result = left * right
		elif func == 'square root':
			result = math.sqrt(left)
		elif func == 'modulo':
			result = left % right
		else:
			result = 'not supported'

		self._lastNumber = result
		return result