import math

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

		self._lastNumber = 0
		self._mathOperations = {
			'+': lambda x,y: x+y,
			'-': lambda x,y: x-y,
			'/': lambda x,y: x/y,
			'*': lambda x,y: x*y,
			'square root': lambda x,_: math.sqrt(x),
			'modulo': lambda x,y: x%y,
			'sine': lambda x,_: round(math.sin(x), 3),
			'cosine': lambda x,_: round(math.cos(x), 3),
			'tangent': lambda x,_: round(math.tan(x), 3)
		}
		super().__init__(self._INTENTS)


	def mathIntent(self, session: DialogSession, **_kwargs):
		mathOperation = session.slots.get('Function')
		left = float(session.slots.get('Left', self._lastNumber))
		right = float(session.slots.get('Right', 0))

		if not mathOperation:
			self.continueDialog(sessionId=session.sessionId, text=self.randomTalk('notUnderstood'))
			return

		self._lastNumber = self._mathOperations[mathOperation](left, right)
		answer = str(self._lastNumber) if self._lastNumber % 1 else str(int(self._lastNumber))
		self.endDialog(sessionId=session.sessionId, text=answer)
