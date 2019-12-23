from core.base.model.Intent import Intent
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Speller(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Ask alice how to spell any word!
	"""

	@IntentHandler('DoSpellWord')
	@IntentHandler('UserRandomAnswer', isProtected=True, requiredState='answerWord')
	def spellIntent(self, session: DialogSession):
		word = session.slotValue('RandomWord', defaultValue='unknownword')

		if word == 'unknownword':
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('notUnderstood'),
				intentFilter=[Intent('UserRandomAnswer')],
				currentDialogState='answerWord'
			)
			return

		string = '<break time="160ms"/>'.join(word)

		self.endDialog(sessionId=session.sessionId, text=self.randomTalk(text='isSpelled', replace=[word, string]))
