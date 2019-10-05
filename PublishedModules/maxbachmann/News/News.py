import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.commons.commons import online, translate


class News(Module):
	"""
	Author: maxbachmann
	Description: Inquire the latest news
	"""

	_INTENT_NEWS = Intent('News')

	def __init__(self):
		self._SUPPORTED_INTENTS	= [
			self._INTENT_NEWS
		]

		super().__init__(self._SUPPORTED_INTENTS)
		self._apiKey = self.getConfig('apiKey')
		self._region = self.getConfig('langCode')
		

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		sessionId = session.sessionId
		slots = session.slotsAsObjects

		try:
			if intent == self._INTENT_NEWS:
				self.endDialog(sessionId, text=self.getNews(slots))
			
		except Exception as e:
			self._logger.error(e)
			self.endDialog(sessionId, text=self.randomTalk('noServer'))

		return True


	@staticmethod
	def queryApi(url: str, *args, **kargs) -> dict:
		return requests.get(url=url.format(*args, **kargs)).json()

	@online
	def getNews(self, slots: dict) -> str:
		if 'number' in slots:
			number = slots['number'].value['value']
		else:
			number = 10
		
		if 'region' in slots:
			region = slots['region'].value['value']
		else:
			region = self._region
		
		if 'category' in slots:
			category = slots['category'].value['value']
		else:
			category = 'general'
		
		articles = self.queryApi(f'https://newsapi.org/v2/top-headlines?country={region}&category={category}&pageSize={number}&apiKey={self._apiKey}')['articles']
		return '<break time=\"400ms\"/>'.join([f"{article['title']}<break time=\"200ms\"/>{article['description']}" for article in articles])
