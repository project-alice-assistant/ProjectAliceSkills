import requests

from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
from core.commons.Commons import online


class IcanhazdadjokeDotCom(Module):
	_INTENT_TELL_A_JOKE = Intent('TellAJoke')

	def __init__(self):
		self._INTENTS = [
			(self._INTENT_TELL_A_JOKE, self.jokeIntent)
		]

		super().__init__(self._INTENTS)


	def offlineHandler(self, session: DialogSession, **_kwargs):
		self.endDialog(session.sessionId, text=self.TalkManager.randomTalk('offline', module='system'))


	@online(offlineHandler=offlineHandler)
	def jokeIntent(self, session: DialogSession, **_kwargs):
		url = 'https://icanhazdadjoke.com/'

		headers = {
			'Accept'    : 'text/plain',
			'User-Agent': 'Project Alice',
			'From'      : 'projectalice@projectalice.ch'
		}

		response = requests.get(url, headers=headers)
		if response is not None:
			self.endDialog(session.sessionId, text=response.text)
		else:
			self.endDialog(session.sessionId, self.TalkManager.getrandomTalk('noJoke'))
