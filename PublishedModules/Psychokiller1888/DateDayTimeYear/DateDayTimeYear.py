from datetime import datetime

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class DateDayTimeYear(Module):
	_INTENT_GET_TIME = Intent('GetTime')
	_INTENT_GET_DATE = Intent('GetDate')
	_INTENT_GET_DAY = Intent('GetDay')
	_INTENT_GET_YEAR = Intent('GetYear')


	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_GET_TIME,
			self._INTENT_GET_DATE,
			self._INTENT_GET_DAY,
			self._INTENT_GET_YEAR
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId

		if intent == self._INTENT_GET_TIME:
			self.timeIntent(sessionId)
		elif intent == self._INTENT_GET_DATE:
			self.dateIntent(sessionId)
		elif intent == self._INTENT_GET_DAY:
			self.dayIntent(sessionId)
		elif intent == self._INTENT_GET_YEAR:
			self.yearIntent(sessionId)

		return True


	def timeIntent(self, sessionId: str):
		minutes = datetime.now().strftime('%M').lstrip('0')
		part = datetime.now().strftime('%p')

		# english has a 12 hour clock and adds oh below 10 min
		if self.LanguageManager.activeLanguage == 'en':
			hours = datetime.now().strftime('%I').lstrip('0')
			if minutes != '' and int(minutes) < 10:
				minutes = 'oh {}'.format(minutes)
		else:
			hours = datetime.now().strftime('%H').lstrip('0')

		self.endDialog(sessionId, self.TalkManager.randomTalk('time').format(hours, minutes, part))


	def dateIntent(self, sessionId: str):
		date = datetime.now().strftime('%d %B %Y')
		date = self.LanguageManager.localize(date)
		self.endDialog(sessionId, self.TalkManager.randomTalk('date').format(date))


	def dayIntent(self, sessionId: str):
		day = datetime.now().strftime('%A')
		day = self.LanguageManager.localize(day)
		self.endDialog(sessionId, self.TalkManager.randomTalk('day').format(day))


	def yearIntent(self, sessionId: str):
		year = datetime.now().strftime('%Y')
		self.endDialog(sessionId, self.TalkManager.randomTalk('day').format(year))
