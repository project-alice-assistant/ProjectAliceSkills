import math
import ast

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Calc(ast.NodeVisitor):

	_OP_MAP = {
		ast.Add: operator.add,
		ast.Sub: operator.sub,
		ast.Mult: operator.mul,
		ast.Div: operator.truediv,
		ast.Invert: operator.neg,
		ast.Pow: operator.pow,
		ast.Mod: operator.mod
	}

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self._OP_MAP[type(node.op)](left, right)

    def visit_Num(self, node):
        return node.n

    def visit_Expr(self, node):
        return self.visit(node.value)

    @classmethod
    def evaluate(cls, expression):
        tree = ast.parse(expression)
        calc = cls()
        return calc.visit(tree.body[0])


class Calculator(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Do some calculation with alice
	"""

	def __init__(self):
		self._lastNumber = 0
		super().__init__()


	def applyCalcToNextKey(self, results: dict, position: int, calc):
		associatedPosition = min(results, key=lambda x:position-x)
		if associatedPosition > position and isinstance(results[associatedPosition], float):
			results[associatedPosition] = calc({results[associatedPosition])


	@IntentHandler('Maths')
	def mathIntent(self, session: DialogSession):
		slots = session.slotsAsObjects

		if not 'Function' in slots:
			self.continueDialog(sessionId=session.sessionId, text=self.randomTalk('notUnderstood'))
			return

		results = {}
		if 'Left' in slots:
			slot = slots['Left'][0]
			position = slot.range['start']
			results[position] = float(slot.value['value'])
		else:
			results[0] = self._lastNumber


		for slot in session.slotsAsObjects.get('Right', [0]):
			position = slot.range['start']
			results[position] = float(slot.value['value'])
		
		for slot in session.slotsAsObjects['Function']:
			position = slot.range['start']
			calc = slot.value['value']
			if calc == '^':
				results[position] = '**'
			elif calc == 'modulo':
				results[position] = '%'
			elif calc == 'square root':
				# square root 25 should be converted to 25**0.5
				applyCalcToNextKey(results, position, lambda number: f'({number} ** 0.5)')
			# sine, cosine and tangent not supported by ast
			elif calc == 'sine':
				applyCalcToNextKey(results, position, math.sin)
			elif calc == 'cosine':
				applyCalcToNextKey(results, position, math.cos)
			elif calc == 'tangent':
				applyCalcToNextKey(results, position, math.tan)
			else:
				results[position] = calc


		cleanedCalculation = ' '.join(str(value) for _, value in sorted(results.items()))
		self._lastNumber = round(Calc.evaluate(cleanedCalculation), 3)

		answer = str(self._lastNumber) if self._lastNumber % 1 else str(int(self._lastNumber))
		self.endDialog(sessionId=session.sessionId, text=answer)
