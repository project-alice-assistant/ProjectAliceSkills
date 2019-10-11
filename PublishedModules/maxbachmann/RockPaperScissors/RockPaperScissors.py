from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class RockPaperScissors(Module):
	"""
	Author: maxbachmann
	Description: Play rock paper scissors
	"""

	_INTENT_ROCK_PAPER_SCISSORS = Intent('RockPaperScissors')

	def __init__(self):
		self._INTENTS = {
			self._INTENT_ROCK_PAPER_SCISSORS: self.rockPaperScissorsIntent
		}

		super().__init__(self._INTENTS)


	def rockPaperScissorsIntent(self, intent: str, session: DialogSession) -> bool:
		randomItem = self.randomTalk(text='RockPaperScissors')
		self.endDialog(session.sessionId, self.randomTalk(text='answer', replace=[randomItem]))
		return True
