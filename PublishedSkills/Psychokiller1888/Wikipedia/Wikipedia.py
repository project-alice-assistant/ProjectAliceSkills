from wikipedia import wikipedia

from core.base.model.Intent import Intent
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler
from core.util.ContextManagers import Online
from core.ProjectAliceExceptions import OfflineError


class Wikipedia(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Allows one to find informations about a topic on wikipedia
	"""

	@staticmethod
	def _extractSearchWord(session: DialogSession) -> str:
		if 'Letters' in session.slots:
			return ''.join([slot.value['value'] for slot in session.slotsAsObjects['Letters']])
		return session.slots.get('What', session.slots.get('RandomWord'))


	def _whatToSearch(self, session: DialogSession, question: str):
		search = self._extractSearchWord(session)
		self.continueDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text=question, replace=[search]),
			intentFilter=[Intent('UserRandomAnswer'), Intent('SpellWord')],
			currentDialogState='whatToSearch'
		)


	@IntentHandler('DoSearch')
	@IntentHandler('UserRandomAnswer', isProtected=True, requiredState='whatToSearch')
	@IntentHandler('SpellWord', isProtected=True, requiredState='whatToSearch')
	def searchIntent(self, session: DialogSession):
		search = self._extractSearchWord(session)
		if not search:
			self._whatToSearch(session, 'whatToSearch')
			return

		wikipedia.set_lang(self.LanguageManager.activeLanguage)

		try:
			with Online():
				result = wikipedia.summary(search, sentences=3)
		except OfflineError:
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('offline', skill='system'))
		except wikipedia.DisambiguationError as e:
			self.logWarning(msg=e)
			self._whatToSearch(session, 'ambiguous')
		except wikipedia.WikipediaException as e:
			self.logWarning(msg=e)
			self._whatToSearch(session, 'noMatch')
		except Exception as e:
			self.logWarning(msg=e, printStack=True)
		else:
			if not result:
				self._whatToSearch(session, 'noMatch')
			else:
				self.endDialog(sessionId=session.sessionId, text=result)
