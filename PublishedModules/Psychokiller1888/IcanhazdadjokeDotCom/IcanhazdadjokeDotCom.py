import requests
from requests.exceptions import RequestException

from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import AnyExcept, IntentHandler, Online


class IcanhazdadjokeDotCom(Module):

	@IntentHandler('TellAJoke')
	@AnyExcept(exceptions=RequestException, text='noJoke', printStack=True)
	@Online
	def jokeIntent(self, session: DialogSession, **_kwargs):
		url = 'https://icanhazdadjoke.com/'

		headers = {
			'Accept'    : 'text/plain',
			'User-Agent': 'Project Alice',
			'From'      : 'projectalice@projectalice.ch'
		}

		response = requests.get(url, headers=headers)
		response.raise_for_status()
		self.endDialog(session.sessionId, text=response.text)
