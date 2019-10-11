from wikipedia import wikipedia

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class Wikipedia(Module):
	"""
	Author: Psychokiller1888
	Description: Allows one to find informations about a topic on wikipedia
	"""

	_INTENT_SEARCH = Intent('DoSearch')
	_INTENT_USER_ANSWER = Intent('UserRandomAnswer', isProtected=True)
	_INTENT_SPELL_WORD = Intent('SpellWord', isProtected=True)


	def __init__(self):
		self._INTENTS = {
			self._INTENT_SEARCH: self.searchIntent,
			self._INTENT_USER_ANSWER: self.randomWordIntent,
			self._INTENT_SPELL_WORD: self.spelledWordIntent
		}

		super().__init__(self._INTENTS)


	def offlineHandler(self, session: DialogSession, *args, **kwargs):
		self.endDialog(session.sessionId, text=self.TalkManager.randomTalk('offline', module='system'))


	def spelledWordIntent(self, intent: str, session: DialogSession):
		word = ''
		for slot in session.slotsAsObjects['Letters']:
			word += slot.value['value']

		if session.previousIntent == self._INTENT_SEARCH
			session.customData['userInput'] = word
			self.searchIntent(intent=intent, session=session)


	def randomWordIntent(self, intent: str, session: DialogSession):
		word = session.slots['RandomWord']

		if session.previousIntent == self._INTENT_SEARCH
			session.customData['userInput'] = word
			self.searchIntent(intent=intent, session=session)


	@online(offlineHandler=offlineHandler)
	def searchIntent(self, intent: str, session: DialogSession):
		slots = session.slots
		sessionId = session.sessionId
		customData = session.customData

		search = customData.get('userInput', slots.get('what'))

		if not search:
			self.continueDialog(
				sessionId=sessionId,
				text=self.randomTalk('whatToSearch'),
				intentFilter=[self._INTENT_USER_ANSWER],
				previousIntent=self._INTENT_SEARCH,
				customData={
					'module': self.name,
				}
			)
			return

		wikipedia.set_lang(self.LanguageManager.activeLanguage)
		engine = customData.get('engine', 'wikipedia')

		try:
			if engine == 'wikipedia':
				result = wikipedia.summary(search, sentences=3)
			else:
				result = wikipedia.summary(search, sentences=3)

			if result:
				self.endDialog(sessionId=sessionId, text=result)
			else:
				self.continueDialog(
					sessionId=sessionId,
					text=self.TalkManager.randomTalk('noMatch').format(search),
					intentFilter=[self._INTENT_USER_ANSWER],
					previousIntent=self._INTENT_SEARCH,
					customData={
						'module': self.name,
						'engine': engine
					}
				)

		except wikipedia.DisambiguationError:
			self.continueDialog(
				sessionId=sessionId,
				text=self.TalkManager.randomTalk('ambiguous').format(search),
				intentFilter=[self._INTENT_USER_ANSWER],
				previousIntent=self._INTENT_SEARCH,
				customData={
					'module': self.name,
					'engine': engine
				}
			)
		except wikipedia.WikipediaException:
			self.continueDialog(
				sessionId=sessionId,
				text=self.TalkManager.randomTalk('noMatch').format(search),
				intentFilter=[self._INTENT_USER_ANSWER],
				previousIntent=self._INTENT_SEARCH,
				customData={
					'module': self.name,
					'engine': engine
				}
			)
		except Exception as e:
			self._logger.error(f'Error: {e}')
			self.endDialog(sessionId=sessionId, text=self.TalkManager.randomTalk('error', module='system'))
