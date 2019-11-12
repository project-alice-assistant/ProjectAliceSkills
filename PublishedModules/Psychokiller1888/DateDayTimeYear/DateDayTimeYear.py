from datetime import datetime

from babel.dates import format_date

from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class DateDayTimeYear(Module):

	@IntentHandler('GetTime')
	def timeIntent(self, session: DialogSession, **_kwargs):
		minutes = datetime.now().minute
		hours = datetime.now().hour

		# english has a 12 hour clock
		if self.LanguageManager.activeLanguage == 'en':

			if minutes < 45:
				if hours == 12:
					hours = 'midday'
				elif hours == 0:
					hours = 'midnight'
				else:
					hours = hours % 12
			else:
				if hours + 1 == 12:
					hours = 'midday'
				elif hours + 1 == 24:
					hours = 'midnight'
				else:
					hours = (hours % 12) + 1

			if minutes > 0:
				if 0 <= minutes < 15 or 15 < minutes < 30 or 30 < minutes < 45:
					answer = f'{minutes} past {hours}'
				elif minutes == 15:
					answer = f'quarter past {hours}'
				elif minutes == 30:
					answer = f'half past {hours}'
				elif minutes == 45:
					answer = f'quarter to {hours}'
				else:
					answer = f'{minutes} to {hours}'
			else:
				answer = f'{hours}'

		elif self.LanguageManager.activeLanguage == 'fr':
			if minutes < 30:
				if hours == 12:
					hours = 'midi'
				elif hours == 0:
					hours = 'minuit'
			else:
				if hours + 1 == 12:
					hours = 'midi'
				elif hours + 1 == 24:
					hours = 'minuit'
				else:
					hours += 1

			if minutes > 0:
				if minutes == 15:
					answer = f'{hours} {"heures" if isinstance(hours, int) else ""} et quart'
				elif minutes == 30:
					if isinstance(hours, int) and hours >= 13:
						answer = f'{hours % 12} {minutes}'
					elif isinstance(hours, str):
						answer = f'{hours} {minutes}'
					else:
						answer = f'{hours} heures et demie'
				elif minutes == 45:
					if isinstance(hours, int) and hours >= 13:
						answer = f'{hours % 12} heures moins quart'
					else:
						answer = f'{hours} moins quart'
				elif minutes > 30:
					answer = f'{hours} {"heures" if isinstance(hours, int) else ""} moins {60 - minutes}'
				else:
					answer = f'{hours} {"heures" if isinstance(hours, int) else ""} {minutes}'
			else:
				answer = f'{hours} {"heures" if isinstance(hours, int) else ""}'


		elif self.LanguageManager.activeLanguage == 'de':
			if minutes == 30:
				hours = (hours % 12) + 1
			elif minutes < 45:
				if hours == 12:
					hours = 'Mittag'
				elif hours == 0:
					hours = 'Mitternacht'
			else:
				if hours + 1 == 12:
					hours = 'Mittag'
				elif hours + 1 == 24:
					hours = 'Mitternacht'

			if minutes > 0:
				if minutes == 15:
					answer = f'viertel nach {hours}'
				elif minutes == 30:
					answer = f'halb {hours}'
				elif minutes == 45:
					answer = f'viertel vor {hours}'
				elif minutes > 45:
					answer = f'{60 - minutes} vor {hours}'
				else:
					answer = f'{minutes} nach {hours}'
			else:
				answer = f'{hours}'
		else:
			answer = f'{hours} {minutes}'

		self.endDialog(session.sessionId, self.TalkManager.randomTalk('time').format(answer))


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
