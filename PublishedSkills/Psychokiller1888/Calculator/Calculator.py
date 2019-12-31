import math

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Calculator(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Do some calculation with alice
	"""

	def __init__(self):
		self._lastNumber = 0
		self._mathOperations = {
			'+'          : lambda x, y: x + y,
			'-'          : lambda x, y: x - y,
			'/'          : lambda x, y: x / y,
			'*'          : lambda x, y: x * y,
			'^'          : lambda x, y: x ** y,
			'square root': lambda x, _: x ** (0, 5),
			'modulo'     : lambda x, y: x % y,
			'sine'       : lambda x, _: math.sin(x),
			'cosine'     : lambda x, _: math.cos(x),
			'tangent'    : lambda x, _: math.tan(x)
		}
		super().__init__()


	@IntentHandler('Maths')
	def mathIntent(self, session: DialogSession):
		mathOperation = self._mathOperations.get(session.slotValue('Function'))
		left = float(session.slotValue('Left', defaultValue=self._lastNumber))
		right = float(session.slotValue('Right', defaultValue=0))

		if not mathOperation:
			self.continueDialog(sessionId=session.sessionId, text=self.randomTalk('notUnderstood'))
			return

		self._lastNumber = round(mathOperation(left, right), 3)
		answer = str(self._lastNumber) if self._lastNumber % 1 else str(int(self._lastNumber))
		self.endDialog(sessionId=session.sessionId, text=answer)
