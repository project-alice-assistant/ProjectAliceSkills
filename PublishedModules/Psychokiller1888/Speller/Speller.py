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
			(self._INTENT_DO_SPELL, self.spellIntent),
			self._INTENT_ANSWER_WORD
		]

		self._INTENT_ANSWER_WORD.dialogMapping = {
			'answerWord': self.spellIntent
		}

		super().__init__(self._SUPPORTED_INTENTS)


	def spellIntent(self, session: DialogSession):
		word = session.slotValue('RandomWord') or 'unknownword'

		if word == 'unknownword':
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('notUnderstood'),
				intentFilter=[self._INTENT_ANSWER_WORD],
				currentDialogState='answerWord'
			)
			return

		string = '<break time="160ms"/>'.join(word)

		self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='isSpelled', replace=[word, string]))
