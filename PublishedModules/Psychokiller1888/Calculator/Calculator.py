import math
import numbers
from typing import Optional

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
		self._INTENTS = [
			(self._INTENT_MATHS, self.mathIntent)
		]
		self._lastNumber: float = 0
		super().__init__(self._INTENTS)


	def mathIntent(self, session: DialogSession, **_kwargs):
		slots = session.slotsAsObjects
		sessionId = session.sessionId

		if ('Left' not in slots and 'Right' not in slots) or 'Function' not in slots:
			self.continueDialog(sessionId=sessionId, text=self.TalkManager.randomTalk('notUnderstood'))
			return

		func = slots['Function'][0].value['value']

		if 'Left' in slots and 'Right' in slots:
			result = self.calculate(float(slots['Left'][0].value['value']), float(slots['Right'][0].value['value']), func)

		elif 'Right' in slots and 'Left' not in slots:
			if not isinstance(self._lastNumber, numbers.Number):
				self.endDialog(sessionId=sessionId, text=self.TalkManager.randomTalk('noPreviousOperation'))
				return

			result = self.calculate(self._lastNumber, float(slots['Right'][0].value['value']), func)

		else:
			self.continueDialog(sessionId=sessionId, text=self.TalkManager.randomTalk('notUnderstood'))
			return

		if not isinstance(result, numbers.Number):
			answer = 'not supported'
		elif result % 1 == 0:
			answer = str(int(result))
		else:
			answer = str(result)

		self.endDialog(sessionId=sessionId, text=answer)


	def calculate(self, left: float, right: float, func: str) -> Optional[float]:
		result: Optional[float] = None
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
			result = math.sin(left)
		elif func == 'cosine':
			result = math.cos(left)
		elif func == 'tangent':
			result = math.tan(left)

		result = round(result, 3)
		self._lastNumber = result
		return result
