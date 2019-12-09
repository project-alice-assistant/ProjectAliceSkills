from typing import Union
from datetime import datetime

from babel.dates import format_date

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler

class DayTime:
	def __init__(self, dt: datetime):
		self._hours = dt.hour
		self._minutes = dt.minute


	@property
	def hours12(self) -> int:
		return self._hours % 12 or 12


	@property
	def hours(self) -> int:
		return self._hours


	@hours.setter
	def hours(self, hours: int):
		self._hours = hours % 24


	@property
	def minutes(self) -> int:
		return self._minutes


	def __str__(self) -> str:
		return f'{self.hours12} {self._minutes}'


class DayTimeEn(DayTime):
	def _stringifyFullHours(self) -> str:
		if self._hours == 12:
			return 'noon'
		if self._hours == 0:
			return 'midnight'

		return f"{self.hours12} o'clock"


	def __str__(self) -> str:
		if self._minutes == 0:
			answer = self._stringifyFullHours()

		elif self._minutes < 10:
			answer = f'{self.hours12} o {self._minutes}'

		elif self._minutes == 15:
			answer = f'quarter past {self.hours12}'

		elif self._minutes == 30:
			answer = f'half past {self.hours12}'

		elif self._minutes == 45:
			self.hours += 1
			answer = f'quarter to {self.hours12}'

		else:
			answer = f'{self.hours12} {self._minutes}'

		return answer


class DayTimeDe(DayTime):
	def _stringifyFullHours(self) -> str:
		if self._hours == 12:
			return 'Mittag'
		if self._hours == 0:
			return 'Mitternacht'

		return f'{self._numberFixup(self.hours12)}'


	@staticmethod
	def _numberFixup(number: int) -> Union[str, int]:
		"""
		The TTS says 'ein' for 1, but for german time it is:
			Es ist eins
		This fixes the number for the tts
		"""
		if number == 1:
			return 'eins'
		return number


	def __str__(self) -> str:
		# Full hour is spoken without minutes and uses Mittag/Mitternacht
		if self._minutes == 0:
			return self._stringifyFullHours()


		# when not a 5min step e.g. 6:21 -> '6 Uhr 21'
		if self._minutes % 5:
			answer = f'{self.hours12} Uhr {self._numberFixup(self._minutes)}'

		# e.g. 6:15 is 'Viertel nach 6'
		# in south germany 'viertel 7' is used aswell, but it confuses many north german people
		# whether this is 6:15 or 6:45 -> not used here
		elif self._minutes == 15:
			answer = f'Viertel nach {self._numberFixup(self.hours12)}'

		# 5 min steps 5, 10, 20 are spoken relative to the current hour
		elif self._minutes <= 20:
			answer = f'{self._minutes} nach {self._numberFixup(self.hours12)}'

		# e.g. 6:25 is spoken relative to the half hour '5 vor halb 7'
		elif self._minutes == 25:
			self.hours += 1
			answer = f'5 vor halb {self._numberFixup(self.hours12)}'

		# e.g. 6:30 is usually spoken as 'halb 7'
		elif self._minutes == 30:
			self.hours += 1
			answer = f'halb {self._numberFixup(self.hours12)}'

		# e.g. 6:35 is spoken relative to the half hour '5 nach halb 7'
		elif self._minutes == 35:
			self.hours += 1
			answer = f'5 nach halb {self._numberFixup(self.hours12)}'

		# e.g. 6:45 is 'Viertel vor 7'
		# in south germany 'dreiviertel 7' is used aswell, but it confuses many north german people
		# whether this is 6:45 or 6:15 -> not used here
		elif self._minutes == 45:
			self.hours += 1
			answer = f'Viertel vor {self._numberFixup(self.hours12)}'

		# 5 min steps 40, 50, 55 are spoken relative to the next full hour
		else:
			self.hours += 1
			answer = f'{60 - self._minutes} vor {self._numberFixup(self.hours12)}'

		#TODO add config option whether it should use am/pm (in german e.g. morgens, mittags, nachmittags abends nachts)
		return answer


class DayTimeFr(DayTime):
	def _stringifyHours(self) -> str:
		if self._hours == 12:
			hour = 'midi'
		elif self._hours == 0:
			hour = 'minuit'
		elif self.hours12 == 1:
			hour = f'{self.hours12} heure'
		else:
			hour = f'{self.hours12} heures'
		return hour


	def __str__(self) -> str:
		if self._minutes > 30:
			self.hours += 1

		hours = self._stringifyHours()

		if self._minutes == 0:
			answer = hours

		elif self._minutes == 15:
			answer = f'{hours} et quart'

		elif self._minutes == 30:
			answer = f'{hours} et demie'

		elif self._minutes == 45:
			answer = f'{hours} moins quart'

		elif self._minutes > 30:
			answer = f'{hours} moins {60 - self._minutes}'

		else:
			answer = f'{hours} {self._minutes}'

		return answer


class DateDayTimeYear(AliceSkill):

	@IntentHandler('GetTime')
	def timeIntent(self, session: DialogSession, **_kwargs):
		if self.LanguageManager.activeLanguage == 'en':
			dayTime: DayTime = DayTimeEn(datetime.now())
		elif self.LanguageManager.activeLanguage == 'fr':
			dayTime = DayTimeFr(datetime.now())
		elif self.LanguageManager.activeLanguage == 'de':
			dayTime = DayTimeDe(datetime.now())
		else:
			dayTime = DayTime(datetime.now())

		self.endDialog(session.sessionId, self.TalkManager.randomTalk('time').format(str(dayTime)))


	@IntentHandler('GetDate')
	def dateIntent(self, session: DialogSession):
		# for english defaults to en_US -> 'November 4, 2019' instead of 4 November 2019 in en_GB
		date = format_date(datetime.now(), format='long', locale=self.LanguageManager.activeLanguage)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('date').format(date))


	@IntentHandler('GetDay')
	def dayIntent(self, session: DialogSession):
		day = format_date(datetime.now(), "EEEE", locale=self.LanguageManager.activeLanguage)
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('day').format(day))


	@IntentHandler('GetYear')
	def yearIntent(self, session: DialogSession):
		year = datetime.now().strftime('%Y')
		self.endDialog(session.sessionId, self.TalkManager.randomTalk('year').format(year))
