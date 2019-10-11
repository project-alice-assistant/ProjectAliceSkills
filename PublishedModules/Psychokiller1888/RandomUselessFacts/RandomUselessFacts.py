import html
import json

import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.commons.commons import online
from core.dialog.model.DialogSession import DialogSession


class RandomUselessFacts(Module):
	"""
	Author: Psychokiller1888
	Description: Gets you the daily random useless fact or a random one
	"""

	_INTENT_GET_USELESS_FACT = Intent('GetUselessFact')


	def __init__(self):
		self._INTENTS = {
			self._INTENT_GET_USELESS_FACT: self.uselessFactIntent
		}

		super().__init__(self._INTENTS)


	def offlineHandler(self, session: DialogSession, **kwargs):
		self.endDialog(session.sessionId, text=self.TalkManager.randomTalk('offline', module='system'))


	@online(offlineHandler=offlineHandler)
	def uselessFactIntent(self, intent: str, session: DialogSession):
		if not 'type' in session.slots:
			ttype = 'random'
		else:
			ttype = session.slotsAsObjects['type'][0].value['value']

		# Try to fetch a fact
		req = requests.request(method='GET', url=f'https://uselessfacts.jsph.pl/{ttype}.json?language={self.activeLanguage()}')
		if req.status_code != 200:
			# Failed, maybe the server is offline?
			self.endDialog(sessionId=session.sessionId, text=self.randomTalk('error'))
		else:
			# Let's load the randomTalk and unescape it as uselessfact seems to encode special characters for german
			self.endDialog(sessionId=session.sessionId, text=html.unescape(req.json()['text']))
