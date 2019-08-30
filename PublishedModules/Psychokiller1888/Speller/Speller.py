# -*- coding: utf-8 -*-

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Speller(Module):
	"""
	Author: Psychokiller1888
	Description: Ask alice how to spell any word!
	"""

	_INTENT_DO_SPELL = Intent('DoSpellWord')
	_INTENT_ANSWER_WORD = Intent('UserRandomAnswer', isProtected=True)

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_DO_SPELL,
			self._INTENT_ANSWER_WORD
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		slots = session.slots

		if intent == self._INTENT_DO_SPELL or (session.previousIntent == self._INTENT_DO_SPELL and intent == self._INTENT_ANSWER_WORD):
			if 'RandomWord' in slots and slots['RandomWord'] != 'unknownword':
				word = slots['RandomWord']
				string = '<break time="160ms"/>'.join(list(word))

				self.endDialog(
					sessionId=sessionId,
					text=self.randomTalk(
						text='isSpelled',
						replace=[word, string]
					)
				)
			else:
				self.continueDialog(
					sessionId=sessionId,
					text=self.randomTalk('notUnderstood'),
					intentFilter=[self._INTENT_ANSWER_WORD],
					previousIntent=self._INTENT_DO_SPELL
				)

		return True
