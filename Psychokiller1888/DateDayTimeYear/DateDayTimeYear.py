# -*- coding: utf-8 -*-

from datetime import datetime

import alice.base.Managers    as managers
from alice.base.model.Intent import Intent
from alice.base.model.Module import Module
from alice.dialog.model.DialogSession import DialogSession


class DateDayTimeYear(Module):

	_INTENT_GET_TIME 	= Intent('hermes/intent/{owner}:GetTime')
	_INTENT_GET_DATE 	= Intent('hermes/intent/{owner}:GetDate')
	_INTENT_GET_DAY 	= Intent('hermes/intent/{owner}:GetDay')
	_INTENT_GET_YEAR 	= Intent('hermes/intent/{owner}:GetYear')


	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_GET_TIME,
			self._INTENT_GET_DATE,
			self._INTENT_GET_DAY,
			self._INTENT_GET_YEAR
		]

		super(DateDayTimeYear, self).__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		siteId = session.siteId
		sessionId = session.sessionId

		if intent == self._INTENT_GET_TIME:
			if managers.LanguageManager.activeLanguage == 'en':
				hours = datetime.now().strftime('%I')
				minutes = datetime.now().strftime('%M')
				part = datetime.now().strftime('%p')

				hours = hours.lstrip('0')
				minutes = minutes.lstrip('0')

				if minutes != '' and int(minutes) < 10:
					minutes = 'oh {}'.format(minutes)

				time = '{} {} {}'.format(hours, minutes, part)
			elif managers.LanguageManager.activeLanguage == 'fr':
				time = datetime.now().strftime('%H heure %M').lstrip('0').replace(' 0', ' ')
			else:
				time = datetime.now().strftime('%H %M').lstrip('0').replace(' 0', ' ')

			managers.MqttServer.endTalk(sessionId, managers.TalkManager.answer(self.name, 'time').format(time), client=siteId)
		elif intent == self._INTENT_GET_DATE:
			date = datetime.now().strftime('%d %B %Y')
			date = managers.LanguageManager.localize(date)
			managers.MqttServer.endTalk(sessionId, managers.TalkManager.answer(self.name, 'date').format(date), client=siteId)
		elif intent == self._INTENT_GET_DAY:
			day = datetime.now().strftime('%A')
			day = managers.LanguageManager.localize(day)
			managers.MqttServer.endTalk(sessionId, managers.TalkManager.answer(self.name, 'day').format(day), client=siteId)
		elif intent == self._INTENT_GET_YEAR:
			year = datetime.now().strftime('%Y')
			managers.MqttServer.endTalk(sessionId, managers.TalkManager.answer(self.name, 'day').format(year), client=siteId)

		return True