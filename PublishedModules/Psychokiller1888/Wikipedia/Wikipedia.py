from typing import Tuple

from wikipedia import wikipedia

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import Decorators


class Wikipedia(Module):
	"""
	Author: Psychokiller1888
	Description: Allows one to find informations about a topic on wikipedia
	"""

	_INTENT_SEARCH = Intent('DoSearch')
	_INTENT_USER_ANSWER = Intent('UserRandomAnswer', isProtected=True)
	_INTENT_SPELL_WORD = Intent('SpellWord', isProtected=True)


	def __init__(self):
		self._INTENTS = [
			(self._INTENT_SEARCH, self.searchIntent),
			self._INTENT_USER_ANSWER,
			self._INTENT_SPELL_WORD
		]

		self._INTENT_USER_ANSWER.dialogMapping = {
			'whatToSearch': self.searchIntent
		}

		self._INTENT_SPELL_WORD.dialogMapping = {
			'whatToSearch': self.searchIntent
		}

		super().__init__(self._INTENTS)


	@staticmethod
	def _extractSlots(session: DialogSession) -> str:
		if 'Letters' in session.slots:
			return ''.join([slot.value['value'] for slot in session.slotsAsObjects['Letters']])
		return session.slots.get('What', session.slots.get('RandomWord'))


	def _whatToSearch(self, session: DialogSession, question: str):
		search = self._extractSearchWord(session)
		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text=question, replace=[search]),
			intentFilter=[self._INTENT_USER_ANSWER, self._INTENT_SPELL_WORD],
			currentDialogState='whatToSearch'
		)


	def noMatchHandler(self, session: DialogSession, **_kwargs):
		self._whatToSearch(session, 'noMatch')


	def ambiguousHandler(self, session: DialogSession, **_kwargs):
		self._whatToSearch(session, 'ambiguous')


	@Decorators.anyExcept(printStack=True)
	@Decorators.anyExcept(exceptions=wikipedia.WikipediaException, exceptHandler=noMatchHandler)
	@Decorators.anyExcept(exceptions=wikipedia.DisambiguationError, exceptHandler=ambiguousHandler)
	@Decorators.online
	def searchIntent(self, session: DialogSession, **_kwargs):
		search = self._extractSearchWord(session)
		if not search:
			self._whatToSearch(session, 'whatToSearch')
			return

		wikipedia.set_lang(self.LanguageManager.activeLanguage)
		result = wikipedia.summary(search, sentences=3)

		if not result:
			self._whatToSearch(session, 'noMatch')
		else:
			self.endDialog(sessionId=session.sessionId, text=result)
