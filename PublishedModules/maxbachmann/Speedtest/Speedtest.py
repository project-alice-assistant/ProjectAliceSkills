import core.base.Managers as managers
from core.base.model.Intent import Intent
from core.base.model.Module import Module
from core.dialog.model.DialogSession import DialogSession
import speedtest

class Speedtest(Module):
	"""
	Author: maxbachmann
	Description: run internet speed test
	"""

	_INTENT_SPEEDTEST = Intent('Speedtest')

	def __init__(self):
		self._SUPPORTED_INTENTS = [
			self._INTENT_SPEEDTEST
		]

		super().__init__(self._SUPPORTED_INTENTS)

	def onMessage(self, intent: str, session: DialogSession) -> bool:
		if not self.filterIntent(intent, session):
			return False

		if intent == self._INTENT_SPEEDTEST:
			try:
				self.say(self.randomTalk(text='running'))
				servers = []
				speed = speedtest.Speedtest()
				speed.get_servers(servers)
				speed.get_best_server()
				speed.download()
				speed.upload(pre_allocate=False)
				speed.results.share()
				result = speed.results.dict()
				downspeed = '{:.2f}'.format(result['download']/1000000)
				upspeed = '{:.2f}'.format(result['upload']/1000000)
				self.endDialog(session.sessionId, self.randomTalk(text='result', replace=[downspeed, upspeed]))
			except:
				self.endDialog(session.sessionId, self.randomTalk(text='failed'))
		return True
