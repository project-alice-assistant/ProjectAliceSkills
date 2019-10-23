import requests
from requests import RequestException

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import Decorators


class News(Module):
	"""
	Author: maxbachmann
	Description: Inquire the latest news
	"""

	_INTENT_NEWS = Intent('News')

	def __init__(self):
		self._INTENTS	= [
			(self._INTENT_NEWS: self.getNews)
		]

		super().__init__(self._INTENTS)
		self._apiKey = self.getConfig('apiKey')
		self._region = self.getConfig('langCode')


	@Decorators.anyExcept(exceptions=(RequestException, KeyError), text='noServer', printStack=True)
	@Decorators.online
	def getNews(self, session: DialogSession, **_kwargs):
		slots = session.slotValue('number') or 10
		region = session.slotValue('region') or self._region
		category = session.slotValue('category') or 'general'

		response = requests.get(url=f'https://newsapi.org/v2/top-headlines?country={region}&category={category}&pageSize={number}&apiKey={self._apiKey}')
		response.raise_for_status()
		articles = response.json()['articles']
		answer = '<break time="400ms"/>'.join([f"{article['title']}<break time=\"200ms\"/>{article['description']}" for article in articles])
		self.endDialog(sessionId=session.sessionId, text=answer)
