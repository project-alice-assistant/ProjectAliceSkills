# -*- coding: utf-8 -*-

import json

from wikipedia import wikipedia

import core.base.Managers as managers
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
		self._SUPPORTED_INTENTS = [
			self._INTENT_SEARCH,
			self._INTENT_USER_ANSWER,
			self._INTENT_SPELL_WORD
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		slots = session.slots
		sessionId = session.sessionId
		customData = session.customData

		if intent == self._INTENT_SEARCH or session.previousIntent == self._INTENT_SEARCH:
			if 'userInput' not in customData and 'what' not in slots:
				if 'engine' not in slots:
					engine = 'wikipedia'
				else:
					engine = slots['engine']

				managers.MqttServer.continueDialog(
					sessionId=sessionId,
					text=managers.TalkManager.randomTalk('whatToSearch'),
					intentFilter=[self._INTENT_USER_ANSWER],
					previousIntent=self._INTENT_SEARCH,
					customData=json.dumps({
						'module': self.name,
						'engine': engine
					})
				)
			else:
				if 'userInput' in customData:
					what = customData['userInput']
				elif 'what' in slots:
					what = slots['what']
				else:
					managers.MqttServer.endTalk(sessionId=sessionId, text=managers.TalkManager.randomTalk('error', module='system'))
					return True

				if intent == self._INTENT_SPELL_WORD:
					search = ''
					for slot in session.slotsAsObjects['Letters']:
						search += slot.value['value']
				else:
					search = what

				wikipedia.set_lang(managers.LanguageManager.activeLanguage)
				if 'engine' in customData:
					engine = customData['engine']
				else:
					engine = 'wikipedia'

				try:
					if engine == 'wikipedia':
						result = wikipedia.summary(search, sentences=3)
					else:
						result = wikipedia.summary(search, sentences=3)
				except wikipedia.DisambiguationError:
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=managers.TalkManager.randomTalk('ambiguous').format(search),
						intentFilter=[self._INTENT_USER_ANSWER],
						previousIntent=self._INTENT_SEARCH,
						customData=json.dumps({
							'module': self.name,
							'engine': engine
						})
					)
					return True
				except wikipedia.WikipediaException:
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=managers.TalkManager.randomTalk('noMatch').format(search),
						intentFilter=[self._INTENT_USER_ANSWER],
						previousIntent=self._INTENT_SEARCH,
						customData=json.dumps({
							'module': self.name,
							'engine': engine
						})
					)
					return True
				except Exception as e:
					self._logger.error('Error: {}'.format(e))
					managers.MqttServer.endTalk(sessionId=sessionId, text=managers.TalkManager.randomTalk('error', module='system'))
					return True

				if result == '':
					managers.MqttServer.continueDialog(
						sessionId=sessionId,
						text=managers.TalkManager.randomTalk('noMatch').format(search),
						intentFilter=[self._INTENT_USER_ANSWER],
						previousIntent=self._INTENT_SEARCH,
						customData=json.dumps({
							'module': self.name,
							'engine': engine
						})
					)
				else:
					managers.MqttServer.endTalk(sessionId=sessionId, text=result)

		return True
