# -*- coding: utf-8 -*-
import core.base.Managers as managers
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
		self._SUPPORTED_INTENTS = [
			self._INTENT_ROCK_PAPER_SCISSORS
		]

		super().__init__(self._SUPPORTED_INTENTS)

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_ROCK_PAPER_SCISSORS:
			randomItem = self.randomTalk(text='RockPaperScissors')
			self.endDialog(session.sessionId, self.randomTalk(text='answer', replace=[randomItem]))

		return True
