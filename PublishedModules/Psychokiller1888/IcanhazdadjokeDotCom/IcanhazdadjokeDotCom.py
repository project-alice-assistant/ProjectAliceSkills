import requests
from requests.exceptions import RequestException

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import AnyExcept, IntentHandler, Online


class IcanhazdadjokeDotCom(AliceSkill):

	@IntentHandler('TellAJoke')
	@AnyExcept(exceptions=RequestException, text='noJoke', printStack=True)
	@Online
	def jokeIntent(self, session: DialogSession):
		url = 'https://icanhazdadjoke.com/'

		headers = {
			'Accept'    : 'text/plain',
			'User-Agent': 'Project Alice',
			'From'      : 'projectalice@projectalice.ch'
		}

		response = requests.get(url, headers=headers)
		response.raise_for_status()
		self.endDialog(session.sessionId, text=response.text)
