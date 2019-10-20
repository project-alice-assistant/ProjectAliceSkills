import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import Decorators


class IcanhazdadjokeDotCom(Module):
	_INTENT_TELL_A_JOKE = Intent('TellAJoke')

	def __init__(self):
		self._INTENTS = [
			(self._INTENT_TELL_A_JOKE, self.jokeIntent)
		]

		super().__init__(self._INTENTS)


	@Decorators.anyExcept(exceptions=RequestException, text='noJoke', printStack=True)
	@Decorators.online
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
