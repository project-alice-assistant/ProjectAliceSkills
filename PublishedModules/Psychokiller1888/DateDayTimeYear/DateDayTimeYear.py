from datetime import datetime
from babel.dates import format_date, format_time

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession


class DateDayTimeYear(Module):
	_INTENT_GET_TIME = Intent('GetTime')
	_INTENT_GET_DATE = Intent('GetDate')
	_INTENT_GET_DAY = Intent('GetDay')
	_INTENT_GET_YEAR = Intent('GetYear')


	def __init__(self):
		self._INTENTS = [
			(self._INTENT_GET_TIME, self.timeIntent),
			(self._INTENT_GET_DATE, self.dateIntent),
			(self._INTENT_GET_DAY, self.dayIntent),
			(self._INTENT_GET_YEAR, self.yearIntent)
		]

		super().__init__(self._INTENTS)


	def timeIntent(self, session: DialogSession, **_kwargs):
		minutes = datetime.now().strftime('%M').lstrip('0')
		part = datetime.now().strftime('%p')

		# english has a 12 hour clock and adds oh below 10 min
		if self.LanguageManager.activeLanguage == 'en':
			hours = f'{datetime.now().hours%12}'
			if minutes != '' and int(minutes) < 10:
				minutes = f'oh {minutes}'
		else:
			hours = f'{datetime.now().hours}'

		self.endDialog(session.sessionId, self.TalkManager.randomTalk('time').format(hours, minutes, part))


	def dateIntent(self, session: DialogSession, **_kwargs):
		# for english defaults to en_US -> 'November 4, 2019' instead of 4 November 2019 in en_GB
		date = format_date(datetime.now(), format='long', locale=self.LanguageManager.activeLanguage)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('date').format(date))


	def dayIntent(self, session: DialogSession, **_kwargs):
		day = format_date(datetime.now(), "EEEE", locale=self.LanguageManager.activeLanguage)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('day').format(day))


	def yearIntent(self, session: DialogSession, **_kwargs):
		year = datetime.now().strftime('%Y')
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('day').format(year))
