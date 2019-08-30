# -*- coding: utf-8 -*-

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

	_INTENT_MATHS = Intent('Maths')


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_MATHS
		]
		self._lastNumber = None
		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		slots = session.slotsAsObjects
		sessionId = session.sessionId

		if intent == self._INTENT_MATHS:
			if ('Left' not in slots and 'Right' not in slots) or 'Function' not in slots:
				self.continueDialog(sessionId=sessionId, text=managers.TalkManager.randomTalk('notUnderstood'))
				return True

			func = slots['Function'][0].value['value']

			if 'Left' in slots and 'Right' in slots:
				result = self.calculate(float(slots['Left'][0].value['value']), float(slots['Right'][0].value['value']), func)

			elif 'Right' in slots and 'Left' not in slots:
				if not self._lastNumber:
					self.endDialog(sessionId=sessionId, text=managers.TalkManager.randomTalk('noPreviousOperation'))
					return True

				result = self.calculate(self._lastNumber, float(slots['Right'][0].value['value']), func)

			else:
				self.continueDialog(sessionId=sessionId, text=managers.TalkManager.randomTalk('notUnderstood'))
				return True

			answer = str(int(result)) if result % 1 == 0 else str(result)

			self.endDialog(sessionId=sessionId, text=answer)

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
		elif func == 'sine':
			result = round(math.sin(left), 3)
		elif func == 'cosine':
			result = round(math.cos(left), 3)
		elif func == 'tangent':
			result = round(math.tan(left), 3)
		else:
			result = 'not supported'

		self._lastNumber = result
		return result
