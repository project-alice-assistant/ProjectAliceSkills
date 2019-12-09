from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class RockPaperScissors(AliceSkill):
	"""
	Author: maxbachmann
	Description: Play rock paper scissors
	"""

	@IntentHandler('RockPaperScissors')
	def rockPaperScissorsIntent(self, session: DialogSession):
		randomItem = self.randomTalk(text='RockPaperScissors')
		self.endDialog(session.sessionId, self.randomTalk(text='answer', replace=[randomItem]))
