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
		self._SUPPORTED_INTENTS	= {
			self._INTENT_DO_SPELL: self.spellIntent,
			self._INTENT_ANSWER_WORD: self.answerWordIntent
		}

		super().__init__(self._SUPPORTED_INTENTS)


	def answerWordIntent(self, intent: str, session: DialogSession) -> bool:
		if session.previousIntent == self._INTENT_DO_SPELL:
			return spellIntent(intent=intent, session=session)
		return False


	def spellIntent(self, intent: str, session: DialogSession) -> bool:
		sessionId = session.sessionId
		slots = session.slots
		word = slots.get('RandomWord', 'unknownword')

		if word != 'unknownword':
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
