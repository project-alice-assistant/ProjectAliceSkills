import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class OpenWeatherMap(Module):
	_INTENT_ANSWER_CITY = Intent('AnswerCity')

	def __init__(self):
		self._INTENTS = {
			self._INTENT_ANSWER_CITY
		}

		self._INTENT_ANSWER_CITY.dialogMapping = {
			'answeringCity': self.getWeather
		}

		super().__init__(self._INTENTS)


	@IntentHandler('GetWeather')
	def getWeather(self, session: DialogSession, **_kwargs):
		city = session.slotRawValue('city') or self.getConfig('baseLocation')

		if 'when' not in session.slots:
			data = self._queryData(city=city)
			if not data:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('notFound').format(city),
					intentFilter=[self._INTENT_ANSWER_CITY],
					slot='city',
					currentDialogState='answeringCity'
				)
			else:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('currentWeather').format(
						city,
						round(float(data['main']['temp']), 1),
						data['weather'][0]['description']
					)
				)
		else:
			# TODO
			self.endSession(sessionId=session.sessionId)


	def _queryData(self, city: str, now: bool = True) -> dict:
		"""
		Queries data from open weather map api
		:param city: string
		:param now: timestamp
		:return: dict()
		"""
		try:
			api = 'weather' if now else 'forecast'

			req = requests.get(url=f'http://api.openweathermap.org/data/2.5/{api}?q={city}&appid={self.getConfig("apiKey")}&lang={self.LanguageManager.activeLanguage}&units={self.getConfig("units")}')
			if req.status_code != 200:
				self.logWarning('API not reachable')
				return dict()

			return req.json()
		except Exception as e:
			self.logWarning(f'Open weather map api call failed: {e}')
			return {}
