from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Speller(Module):
	"""
	Author: Psychokiller1888
	Description: Ask alice how to spell any word!
	"""

	@IntentHandler('DoSpellWord')
	@IntentHandler('UserRandomAnswer', requiredState='answerWord', isProtected=True)
	def spellIntent(self, session: DialogSession, **_kwargs):
		word = session.slotValue('RandomWord') or 'unknownword'

		if word == 'unknownword':
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('notUnderstood'),
				intentFilter=[self._INTENT_ANSWER_WORD],
				currentDialogState='answerWord'
			)
			return

		string = '<break time="160ms"/>'.join(list(word))

		self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='isSpelled', replace=[word, string]))
