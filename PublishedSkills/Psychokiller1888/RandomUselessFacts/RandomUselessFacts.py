import html

import requests
from requests.exceptions import RequestException

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import AnyExcept, IntentHandler, Online


class RandomUselessFacts(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Gets you the daily random useless fact or a random one
	"""

	@IntentHandler('GetUselessFact')
	@AnyExcept(exceptions=(RequestException, KeyError), text='error', printStack=True)
	@Online
	def uselessFactIntent(self, session: DialogSession):
		ttype = session.slotValue('type', defaultValue='random')

		response = requests.get(url=f'https://uselessfacts.jsph.pl/{ttype}.json?language={self.activeLanguage()}')
		response.raise_for_status()
		self.endDialog(sessionId=session.sessionId, text=html.unescape(response.json()['text']))
