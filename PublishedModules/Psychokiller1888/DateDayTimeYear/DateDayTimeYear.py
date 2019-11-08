from datetime import datetime
from babel.dates import format_date

from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class DateDayTimeYear(Module):

	@IntentHandler('GetTime')
	def timeIntent(self, session: DialogSession, **_kwargs):
		minutes = datetime.now().strftime('%M').lstrip('0')
		part = datetime.now().strftime('%p')

		# english has a 12 hour clock and adds oh below 10 min
		if self.LanguageManager.activeLanguage == 'en':
			hours = f'{datetime.now().hour%12}'
			if minutes != '' and int(minutes) < 10:
				minutes = f'oh {minutes}'
		else:
			hours = f'{datetime.now().hour}'

		self.endDialog(session.sessionId, self.TalkManager.randomTalk('time').format(hours, minutes, part))


	@IntentHandler('GetDate')
	def dateIntent(self, session: DialogSession, **_kwargs):
		# for english defaults to en_US -> 'November 4, 2019' instead of 4 November 2019 in en_GB
		date = format_date(datetime.now(), format='long', locale=self.LanguageManager.activeLanguage)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('date').format(date))


	@IntentHandler('GetDay')
	def dayIntent(self, session: DialogSession, **_kwargs):
		day = format_date(datetime.now(), "EEEE", locale=self.LanguageManager.activeLanguage)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('day').format(day))


	@IntentHandler('GetYear')
	def yearIntent(self, session: DialogSession, **_kwargs):
		year = datetime.now().strftime('%Y')
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('day').format(year))
