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
		self._SUPPORTED_INTENTS = [
			self._INTENT_GET_USELESS_FACT
		]

		super().__init__(self._SUPPORTED_INTENTS)


	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_GET_USELESS_FACT:
			if not 'type' in session.slots:
				ttype = 'random'
			else:
				ttype = session.slotsAsObjects['type'][0].value['value']

			self.endDialog(sessionId=session.sessionId, text=self.getAFact(ttype=ttype))

		return True

	@online
	def getAFact(self, ttype: str) -> str:
		# Try to fetch a fact
		req = requests.request(method='GET', url='https://uselessfacts.jsph.pl/{}.json?language={}'.format(ttype, self.activeLanguage()))
		if req.status_code != 200:
			# Failed, maybe the server is offline?
			return self.randomTalk('error')
		else:
			# Let's load the randomTalk and unescape it as uselessfact seems to encode special characters for german
			return html.unescape(json.loads(req.content)['text'])
