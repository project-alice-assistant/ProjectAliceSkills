import requests

from core.base.model.Intent import Intent
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class OpenWeatherMap(AliceSkill):

	@IntentHandler('GetWeather')
	@IntentHandler('AnswerCity', requiredState='answeringCity')
	def getWeather(self, session: DialogSession):

		if not self.getConfig('apiKey'):
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk('noApiKey')
			)
			return

		city = session.slotRawValue('City') or self.getConfig('baseLocation')

		if 'when' not in session.slots:
			data = self._queryData(city=city)
			if not data:
				self.continueDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('notFound', replace=[city]),
					intentFilter=[Intent('AnswerCity')],
					slot='City',
					currentDialogState='answeringCity'
				)
			else:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk('currentWeather',
					                     replace=[
						                     city,
						                     round(float(data['main']['temp']), 1),
						                     data['weather'][0]['description']
					                     ]
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
