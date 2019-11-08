from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class RockPaperScissors(Module):
	"""
	Author: maxbachmann
	Description: Play rock paper scissors
	"""

	@IntentHandler('RockPaperScissors')
	def rockPaperScissorsIntent(self, session: DialogSession, **_kwargs):
		randomItem = self.randomTalk(text='RockPaperScissors')
		self.endDialog(session.sessionId, self.randomTalk(text='answer', replace=[randomItem]))
